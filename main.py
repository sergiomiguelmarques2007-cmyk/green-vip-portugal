import os
import requests
from datetime import datetime
from zoneinfo import ZoneInfo

# Configurações privadas, guardadas no GitHub Secrets
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
FOOTBALL_API_KEY = os.getenv("FOOTBALL_API_KEY")

API_URL = "https://v3.football.api-sports.io"


def enviar_telegram(mensagem):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        raise ValueError("Falta configurar o Telegram.")

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    resposta = requests.post(
        url,
        json={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": mensagem
        },
        timeout=30
    )

    resposta.raise_for_status()


def obter_jogos():
    if not FOOTBALL_API_KEY:
        raise ValueError("Falta a chave da API de futebol.")

    hoje = datetime.now(ZoneInfo("Europe/Lisbon")).date()

    resposta = requests.get(
        f"{API_URL}/fixtures",
        headers={"x-apisports-key": FOOTBALL_API_KEY},
        params={"date": str(hoje)},
        timeout=30
    )

    resposta.raise_for_status()
    return resposta.json().get("response", [])


def analisar_jogos():
    jogos = obter_jogos()

    if not jogos:
        enviar_telegram(
            "⚽ GREEN VIP PORTUGAL\n\n"
            "Não foram encontrados jogos para hoje."
        )
        return

    mensagem = [
        "⚽ GREEN VIP PORTUGAL",
        "📊 RELATÓRIO DE FUTEBOL",
        "",
        "⚠️ Análise informativa, sem greens garantidos."
    ]

    for jogo in jogos:
        casa = jogo["teams"]["home"]["name"]
        fora = jogo["teams"]["away"]["name"]
        liga = jogo["league"]["name"]
        estado = jogo["fixture"]["status"]["short"]
        golos_casa = jogo["goals"]["home"]
        golos_fora = jogo["goals"]["away"]

        if estado == "FT":
            mensagem.append(
                f"\n🟢 RESULTADO FINAL\n"
                f"{casa} {golos_casa}-{golos_fora} {fora}\n"
                f"🏆 {liga}"
            )

        elif estado in ("1H", "2H", "HT", "ET", "P"):
            mensagem.append(
                f"\n🔴 JOGO EM DIRETO\n"
                f"{casa} {golos_casa}-{golos_fora} {fora}\n"
                f"🏆 {liga}"
            )

        else:
            hora = jogo["fixture"]["date"][11:16]

            mensagem.append(
                f"\n⚽ {casa} - {fora}\n"
                f"🏆 {liga}\n"
                f"🕒 Hora UTC: {hora}\n"
                f"📊 A aguardar análise estatística."
            )

    enviar_telegram("\n".join(mensagem))


if __name__ == "__main__":
    analisar_jogos()
