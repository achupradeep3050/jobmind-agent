module.exports = {
  apps: [
    {
      name: "jobmind",
      script: "python",
      // ── IMPORTANT: Edit args/cwd/env for YOUR machine ──
      // python_path:    Path to your Python 3.11+ virtual environment
      // cwd:            Path to the job-application-agent directory
      // PYTHONPATH:     Must include ./src and your site-packages
      args: "-m streamlit run app.py --server.headless=false --server.port=8501 --server.headless=true",
      interpreter: "none",
      env: {
        // EDIT THESE FOR YOUR SYSTEM:
        PYTHONPATH: "./src:$HOME/.hermes/hermes-agent/venv/lib/python3.11/site-packages",
        PATH: "$HOME/.hermes/hermes-agent/venv/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin",
        STREAMLIT_SERVER_HEADLESS: "true",
        STREAMLIT_BROWSER_GATHER_USAGE_STATS: "false",
        STREAMLIT_SERVER_PORT: "8501",
        // Set your Blackbox API key here, or via .env / .env.local
        // BLACKBOX_API_KEY: "sk-your-key-here",
      },
      watch: false,
      autorestart: true,
      max_restarts: 10,
      max_memory: "1G",
    },
  ],
};