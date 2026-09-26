# Kubernetes

The chatbot keeps anything persistent in `/app/data`. That directory exists in the image and
is writable, so a volume is optional — without one you lose the data on every restart.

## Storage

    apiVersion: v1
    kind: PersistentVolumeClaim
    metadata:
      name: discord-data
      namespace: discord
    spec:
      storageClassName: local-path-retain
      accessModes: [ReadWriteOnce]
      resources:
        requests:
          storage: 1Gi

Get `storageClassName` right the first time. k3s defaults to `local-path`, which has
`reclaimPolicy: Delete` — deleting the claim erases the data, and since directories are
named after the PVC UID, recreating it gets you an empty one. Changing the class later
means deleting and recreating the PVC, which is the event you were avoiding.

If the cluster has no Retain class yet:

    apiVersion: storage.k8s.io/v1
    kind: StorageClass
    metadata:
      name: local-path-retain
    provisioner: rancher.io/local-path
    reclaimPolicy: Retain
    volumeBindingMode: WaitForFirstConsumer

Retain makes deletion recoverable, not harmless — you still dig the directory out of the
node by hand.

The 1Gi is a formality; local-path hands out a node directory and ignores the number.
`ReadWriteOnce` is fine because the Deployment only ever runs one replica.

### Adding a volume to a running chatbot

Applying the volume replaces the pod and throws away the database inside it. Copy it out
first:

    POD=$(kubectl get pod -n discord -l app=discord -o name | cut -d/ -f2)
    kubectl cp -n discord "$POD":/app/data/krillion.db ./krillion.db

Apply the PVC and Deployment, wait for the new pod, then copy it back and restart so
SQLite reopens the file:

    POD=$(kubectl get pod -n discord -l app=discord -o name | cut -d/ -f2)
    kubectl cp -n discord ./krillion.db "$POD":/app/data/krillion.db
    kubectl rollout restart deploy/discord -n discord

Keep the local copy until you've confirmed the scores are back.

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

`readOnlyRootFilesystem` works because the image sets `LOG_FILE=""` and logs to stdout.
Point `LOG_FILE` at a path again and the bot dies on startup trying to open it. It also
makes the volume mandatory — with a read-only root there is nowhere to put the database.

`Recreate` avoids the rolling update briefly running two pods on one token, which makes
them disconnect each other in a loop, and keeps two processes off the same SQLite file.

No Service or Ingress — the bot only makes outbound connections.

## Pinning the image

`:latest` moves on every push to main, and `imagePullPolicy: IfNotPresent` means a node
that already has it won't pull again. Pin the immutable tag instead:

    image: ghcr.io/ottter/discord-bot:sha-1a2b3c4

## Checking it worked

    kubectl logs -n discord deploy/discord --tail=20

    Krillion database ready at /app/data/krillion.db
    Loaded 6 extension(s): copypasta, eightball, errors, on_ready, version, krillion
    Online as yourbot#1234 (123456789) | prefix , | 24 ms | 1 guild(s): Your Server
    Synced 5 slash command(s): 8ball, fbi, hello, krillion, version

To prove the volume works, submit a score, `kubectl rollout restart deploy/discord -n
discord`, and check it survived. If it didn't, the database path in the log is pointing
somewhere other than `/app/data`.
