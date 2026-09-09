from google import genai
client = genai.Client(api_key="AIzaSyDaKrCqBKtDt08rSjB72psQNN5k95zb-OI")
for m in client.models.list():
    print(f"Modelo disponível: {m.name}")
