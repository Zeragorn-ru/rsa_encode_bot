if [ ! -e ./.env ]; then
  touch .env
  echo "BOT_TOKEN=$1" >> .env
  echo "ADMINS=$2" >> .env
fi

if [ ! -e ./.rsa_encode_bot_env ]; then
  python3.13 -m venv .rsa_encode_bot_env
  source .rsa_encode_bot_env/bin/activate
  pip install -r req.txt
  deactivate
fi

