# Public deployment without a tunnel password

1. Push the repository to GitHub.
2. Open [Render's FINN Blueprint](https://render.com/deploy?repo=https://github.com/WaqarMoid/finn-investment-agent).
3. Sign in to Render and authorize the repository if prompted.
4. Accept the Blueprint and wait for the Docker build and health check.
5. Open the generated `https://finn-investment-agent-<suffix>.onrender.com` URL on the phone.

The link uses managed HTTPS and requires no IP or tunnel password. A free instance may take roughly a minute to wake after inactivity. The included `render.yaml` uses live NSE mode and an ephemeral SQLite database that rebuilds on startup.

For a durable production deployment, attach a Render persistent disk at `/data`, set `DATA_DIR=/data`, and set `DATABASE_PATH=/data/finn.db`.
