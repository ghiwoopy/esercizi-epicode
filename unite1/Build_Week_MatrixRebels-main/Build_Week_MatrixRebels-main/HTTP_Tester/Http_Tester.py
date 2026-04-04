aimport requests # Libreria per inviare richieste HTTP (GET, POST, ecc.)
from datetime import datetime  # Serve per salvare data e ora nei risultati


def interpreta_status(code):
    """Restituisce una breve spiegazione del codice HTTP."""

    # Dizionario che associa ogni codice HTTP a una spiegazione
    spiegazioni = {
        200: "OK - richiesta completata con successo",
        201: "Created - risorsa creata con successo",
        202: "Accepted - richiesta accettata",
        204: "No Content - richiesta riuscita senza contenuto",
        301: "Moved Permanently - redirect permanente",
        302: "Found - redirect temporaneo",
        400: "Bad Request - richiesta non valida",
        401: "Unauthorized - autenticazione richiesta",
        403: "Forbidden - accesso vietato",
        404: "Not Found - risorsa non trovata",
        405: "Method Not Allowed - metodo non consentito",
        408: "Request Timeout - richiesta scaduta",
        500: "Internal Server Error - errore interno del server",
        501: "Not Implemented - metodo non implementato",
        502: "Bad Gateway - gateway non valido",
        503: "Service Unavailable - servizio non disponibile",
    }

    # Restituisce la spiegazione se esiste, altrimenti una generica
    return spiegazioni.get(code, "Codice non classificato")


def costruisci_url(base_url, path):
    """Unisce correttamente URL base e path."""

    # Rimuove eventuali "/" in eccesso e unisce correttamente
    return base_url.rstrip("/") + "/" + path.lstrip("/")


def invia_richiesta(method, url):
    """
    Invia una richiesta HTTP al server.
    Per POST, PUT e DELETE usa un body di test.
    """

    try:
        # Header HTTP (identifica il client)
        headers = {
            "User-Agent": "Theta-HTTP-Tester/1.0"
        }

        # Dati fittizi usati per test (POST/PUT/DELETE)
        data = {"test": "theta"}

        # Se il metodo richiede dati
        if method in ["POST", "PUT", "DELETE"]:
            response = requests.request(
                method,
                url,
                headers=headers,
                data=data,
                timeout=5,  # timeout per evitare blocchi
                allow_redirects=False  # non segue redirect automaticamente
            )
        else:
            # Per GET, HEAD, OPTIONS
            response = requests.request(
                method,
                url,
                headers=headers,
                timeout=5,
                allow_redirects=False
            )

        # Restituisce tutte le informazioni utili in un dizionario
        return {
            "metodo": method,
            "status_code": response.status_code,  # codice HTTP
            "significato": interpreta_status(response.status_code),  # spiegazione
            "allow": response.headers.get("Allow", "-"),  # metodi consentiti
            "server": response.headers.get("Server", "-"),  # info server
            "content_type": response.headers.get("Content-Type", "-"),  # tipo contenuto
            "lunghezza": len(response.text) if response.text else 0,  # dimensione risposta
            "errore": "-"
        }

    # Se c'è un errore (timeout, connessione, ecc.)
    except requests.exceptions.RequestException as e:
        return {
            "metodo": method,
            "status_code": "ERRORE",
            "significato": "Richiesta non completata",
            "allow": "-",
            "server": "-",
            "content_type": "-",
            "lunghezza": 0,
            "errore": str(e)
        }


def stampa_risultati(results, url):
    """Stampa i risultati in modo ordinato."""

    print("\n" + "=" * 80)
    print("RISULTATI HTTP TESTER")
    print("=" * 80)
    print(f"Target testato: {url}")
    print("-" * 80)

    # Scorre tutti i risultati e li stampa
    for r in results:
        print(f"Metodo       : {r['metodo']}")
        print(f"Status code  : {r['status_code']}")
        print(f"Significato  : {r['significato']}")
        print(f"Allow        : {r['allow']}")
        print(f"Server       : {r['server']}")
        print(f"Content-Type : {r['content_type']}")
        print(f"Lunghezza    : {r['lunghezza']} byte")
        print(f"Errore       : {r['errore']}")
        print("-" * 80)


def salva_risultati(results, url, filename="risultati_http.txt"):
    """Salva i risultati su file di testo."""

    with open(filename, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("RISULTATI HTTP TESTER\n")
        f.write("=" * 80 + "\n")
        f.write(f"Data test: {datetime.now()}\n")  # salva data e ora
        f.write(f"Target testato: {url}\n")
        f.write("-" * 80 + "\n")

        # Scrive ogni risultato nel file
        for r in results:
            f.write(f"Metodo       : {r['metodo']}\n")
            f.write(f"Status code  : {r['status_code']}\n")
            f.write(f"Significato  : {r['significato']}\n")
            f.write(f"Allow        : {r['allow']}\n")
            f.write(f"Server       : {r['server']}\n")
            f.write(f"Content-Type : {r['content_type']}\n")
            f.write(f"Lunghezza    : {r['lunghezza']} byte\n")
            f.write(f"Errore       : {r['errore']}\n")
            f.write("-" * 80 + "\n")

    print(f"\nRisultati salvati in '{filename}'")


def analisi_finale(results):
    """Produce una breve analisi finale."""

    print("\n" + "=" * 80)
    print("ANALISI FINALE")
    print("=" * 80)

    # Liste per classificare i metodi
    metodi_ok = []
    metodi_bloccati = []
    metodi_errore = []

    for r in results:
        if isinstance(r["status_code"], int):
            if r["status_code"] < 400:
                metodi_ok.append(r["metodo"])  # metodo funzionante
            elif r["status_code"] == 405:
                metodi_bloccati.append(r["metodo"])  # metodo vietato
            else:
                metodi_errore.append(f"{r['metodo']} ({r['status_code']})")
        else:
            metodi_errore.append(f"{r['metodo']} (ERRORE)")

    # Stampa riepilogo
    print(f"Metodi con risposta positiva o utile: {', '.join(metodi_ok) if metodi_ok else 'Nessuno'}")
    print(f"Metodi non consentiti: {', '.join(metodi_bloccati) if metodi_bloccati else 'Nessuno'}")
    print(f"Metodi con errore o risposta critica: {', '.join(metodi_errore) if metodi_errore else 'Nessuno'}")


def main():
    print("=== HTTP TESTER DI THETA ===")

    # Input utente
    base_url = input("Inserisci URL base (es. http://192.168.1.10): ").strip()
    path = input("Inserisci il path da testare (es. /phpMyAdmin): ").strip()

    # Costruisce URL completo
    url = costruisci_url(base_url, path)

    # Metodi HTTP da testare
    methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"]

    results = []

    print(f"\nTest in corso su: {url}")
    print("Metodi testati:", ", ".join(methods))

    # Esegue il test per ogni metodo
    for method in methods:
        risultato = invia_richiesta(method, url)
        results.append(risultato)

    # Stampa risultati
    stampa_risultati(results, url)

    # Analisi finale
    analisi_finale(results)

    # Chiede se salvare su file
    save = input("\nVuoi salvare i risultati su file? (s/n): ").strip().lower()

    risposte_si = {"s", "si", "sì", "y", "yes"}

    if save in risposte_si:
     salva_risultati(results, url)
    else:
     print("Operazione annullata.")


# Punto di ingresso del programma
if __name__ == "__main__":
    main()