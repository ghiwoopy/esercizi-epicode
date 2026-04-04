import socket #Serve per usare le funzioni di rete di Python.
import time #Serve per misurare il tempo impiegato dalla scansione.
import threading # Permette di eseguire più operazioni contemporaneamente
from queue import Queue # Struttura dati usata per gestire in modo ordinato le porte da scansionare tra i thread

# Coda delle porte da scansionare
port_queue = Queue() #evita che due thread prendano la stessa porta

results = [] # Questa è una lista vuota che servirà per salvare i risultati della scansione.


lock = threading.Lock() # Lock per evitare problemi quando più thread scrivono insieme



def scan_port(target_ip): #Ogni thread esegue questa funzione.
    while not port_queue.empty(): #Finché ci sono porte da scansionare, continua a prendere una porta dalla coda e a scansionarla.
        port = port_queue.get()  #Qui il thread prende una porta dalla coda.

        try: #Questo blocco serve a gestire eventuali errori di rete senza far crashare il programma.
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Crea un socket TCP/IP per la comunicazione con il target.
            s.settimeout(0.5)  # timeout più basso per una maggiore velocità

            result = s.connect_ex((target_ip, port)) #Prova a connettersi alla porta specificata. Se la connessione riesce, restituisce 0, altrimenti un codice di errore.
            if result == 0:
                try:
                    service = socket.getservbyport(port) #Prova a identificare il servizio associato alla porta. 
                except:
                    service = "Servizio sconosciuto"

                banner = ""
                try:
                    s.send(b"HELLO\r\n")
                    banner = s.recv(1024).decode(errors="ignore").strip() #Prova a inviare un messaggio alla porta e a ricevere una risposta (banner). Se la porta risponde, il banner può fornire informazioni sul servizio in esecuzione.
                except:
                    banner = "Nessun banner ricevuto"

                with lock:
                    print(f"[APERTA] Porta {port} | Servizio: {service} | Banner: {banner}") #Stampa a video le informazioni sulla porta aperta. Il lock serve a evitare che più thread stampino contemporaneamente e mescolino le informazioni.
                    results.append({
                        "porta": port,
                        "stato": "APERTA",
                        "servizio": service,
                        "banner": banner
                    })

            else:
                with lock:
                    results.append({
                        "porta": port,
                        "stato": "CHIUSA",
                        "servizio": "-",
                        "banner": "-"
                    })

            s.close()

        except socket.error: #Se c'è un errore di rete (ad esempio, il target è irraggiungibile), viene gestito qui.
            with lock:
                results.append({
                    "porta": port,
                    "stato": "ERRORE",
                    "servizio": "-",
                    "banner": "-"
                })

        port_queue.task_done()


def main():
    print("=== BENVENUTO NEL PORT SCANNER DI THETA===") #Messaggio di benvenuto per l'utente.

    target = input("Prego inserisci IP o hostname target: ").strip()

    try:
        target_ip = socket.gethostbyname(target) #Prova a risolvere l'hostname in un indirizzo IP. Se l'utente ha inserito un hostname, questa funzione lo converte in un IP. Se l'hostname non è valido o non può essere risolto, viene sollevata un'eccezione.
    except socket.gaierror:
        print("Impossibile risolvere il target.")
        return

    try:
        start_port = int(input("Porta iniziale: "))
        end_port = int(input("Porta finale: "))
    except ValueError:
        print("Errore: inserire numeri interi.")
        return

    if start_port < 1 or end_port > 65535 or start_port > end_port: #Controlla che le porte inserite siano valide (tra 1 e 65535) e che la porta iniziale non sia maggiore di quella finale. Se c'è un errore, stampa un messaggio e termina il programma.
        print("Intervallo porte non valido.")
        return

    print(f"\nTarget: {target} ({target_ip})")
    print(f"Scansione porte da {start_port} a {end_port}")
    print("-" * 60)

    start_time = time.time()

   
    for port in range(start_port, end_port + 1):  # Le porte vengono messe in una coda, così i thread le prendono una per volta finché finiscono il lavoro.
        port_queue.put(port)

   
    num_threads = 50  # Qui fai partire 50 controlli quasi in parallelo

    threads = []
    for _ in range(num_threads):
        thread = threading.Thread(target=scan_port, args=(target_ip,))
        thread.start()
        threads.append(thread)

   
    port_queue.join()  # Attende che la coda venga svuotata

    end_time = time.time() #Misura il tempo di fine scansione per calcolare quanto tempo è stato impiegato.
    print("\n" + "=" * 60)
    print("SCANSIONE COMPLETATA")
    print("=" * 60)

    open_ports = [r for r in results if r["stato"] == "APERTA"] #Filtra i risultati per mostrare solo le porte aperte. Crea una nuova lista che contiene solo i dizionari dei risultati in cui lo stato è "APERTA".
    if open_ports:
        print("\nPorte aperte trovate:")
        for r in sorted(open_ports, key=lambda x: x["porta"]):
            print(f"- Porta {r['porta']} | Servizio: {r['servizio']} | Banner: {r['banner']}") 
    else:
        print("\nNessuna porta aperta trovata.")

    print(f"\nTempo totale di scansione: {end_time - start_time:.2f} secondi")


if __name__ == "__main__":
    main()