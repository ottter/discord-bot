# Kubernetes

Anything the bot needs to keep goes in `/app/data` — today that's the Krillion score
database, and whatever a later feature stores will land beside it. The directory exists
in the image and is writable, but a container filesystem is thrown away on restart, so
without a volume that data lasts only as long as the pod.

## Storage

The volume is optional. `/app/data` exists in the image and is writable, so the bot runs
fine without one — you just lose whatever is in there each time the pod restarts. For
scores nobody is attached to yet, that is a reasonable trade; add the claim when the
data starts mattering.

    apiVersion: v1
    kind: PersistentVolumeClaim
    metadata:
      name: discord-data
      namespace: discord
    spec:
      accessModes: [ReadWriteOnce]
      resources:
        requests:
          storage: 1Gi

1Gi is far more than a Discord bot's bookkeeping needs, but most provisioners round up
to a minimum anyway, and it leaves room for whatever gets added later.

`ReadWriteOnce` is correct here and not a limitation: Discord allows one gateway
connection per token, so the Deployment runs a single replica regardless.

### Losing data to a deleted PVC

Check what your storage class does when a PVC goes away:

    kubectl get storageclass

A class with `reclaimPolicy: Delete` erases the backing data immediately. On k3s the
built-in `local-path` does exactly that, and because it names directories after the PVC
UID, recreating the claim gets you a new empty one — the old data is still on disk but
effectively unreachable.

If that matters, point the claim at a class with `reclaimPolicy: Retain`:

    spec:
      storageClassName: local-path-retain
      accessModes: [ReadWriteOnce]

Recovery then means finding the directory on the node by hand, but it is still there to
find.

## Deployment

    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: discord
      namespace: discord
    spec:
      replicas: 1                 # one gateway connection per token
      strategy:
        type: Recreate            # never two pods on the same token
      selector:
        matchLabels:
          app: discord
      template:
        metadata:
          labels:
            app: discord
        spec:
          containers:
            - name: discord
              image: ghcr.io/ottter/discord-bot:latest
              env:
                - name: DISCORD_TOKEN
                  valueFrom:
                    secretKeyRef:
                      name: discord-secrets
                      key: DISCORD_TOKEN
              volumeMounts:
                - name: data
                  mountPath: /app/data
              resources:
                requests: {cpu: 10m, memory: 64Mi}
                limits: {memory: 256Mi}
              securityContext:
                runAsNonRoot: true
                readOnlyRootFilesystem: true
                allowPrivilegeEscalation: false
                capabilities:
                  drop: ["ALL"]
          volumes:
            - name: data
              persistentVolumeClaim:
                claimName: discord-data

`readOnlyRootFilesystem: true` works because the image logs to stdout instead of a file.
It is also the one setting that makes the volume mandatory: with a read-only root there
is nowhere to create the database, and the bot fails on startup. Leave it out, or leave
the mount in.

`Recreate` matters more than it looks. The default rolling update briefly runs the old
and new pods together, and two connections on one token disconnect each other in a loop.
It also keeps two processes off the same SQLite file.

No Service or Ingress: the bot opens an outbound connection to Discord and listens on
nothing.

## Pinning the image

`:latest` moves whenever main is pushed, and with `imagePullPolicy: IfNotPresent` a node
that already has an image by that name will not pull the new one. Every build also gets
an immutable `sha-<commit>` tag, which is the one to use when you want a deploy to be
reproducible and a rollback to be one edit:

    image: ghcr.io/ottter/discord-bot:sha-1a2b3c4

## Checking it worked

    kubectl logs -n discord deploy/discord --tail=20

A healthy start names anything it opened under `/app/data`, then the guilds it connected
to:

    Krillion database ready at /app/data/krillion.db
    Loaded 4 extension(s): copypasta, eightball, on_ready, krillion
    Online as yourbot#1234 (123456789) | prefix , | 24 ms | 1 guild(s): Your Server
    Synced 4 slash command(s): 8ball, fbi, hello, krillion

To confirm the volume is really doing its job, write something the bot persists — a
Krillion score, say — then restart it:

    kubectl rollout restart deploy/discord -n discord

If it survives, the mount is working. If it doesn't, the paths in the startup log will
be pointing somewhere other than `/app/data`.
