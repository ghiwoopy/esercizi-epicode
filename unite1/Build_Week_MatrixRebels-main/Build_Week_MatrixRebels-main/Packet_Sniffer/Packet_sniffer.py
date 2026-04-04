import socket  # Libreria per lavorare con la rete (socket TCP/IP)

# Creazione del socket RAW
# AF_INET → IPv4
# SOCK_RAW → permette di catturare direttamente i pacchetti di rete
# IPPROTO_TCP → filtra solo i pacchetti TCP
sniffer = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)

# Messaggio iniziale per indicare che il programma è attivo
print("=== SNIFFER DI RETE ATTIVO ===")
print("Premere CTRL+C per interrompere...\n")

# Ciclo infinito: il programma resta in ascolto continuo
while True:

    # recvfrom cattura un pacchetto dalla rete
    # 65536 è la dimensione massima del pacchetto (in byte)
    raw_data, addr = sniffer.recvfrom(65536)

    # raw_data → contiene i dati grezzi del pacchetto
    # addr → contiene informazioni sull'indirizzo sorgente

    print("========================================")

    # Indirizzo IP del mittente
    print(f"IP sorgente: {addr[0]}")

    # Indirizzo IP locale (dove arriva il pacchetto)
    print(f"IP destinazione (locale): {addr[1]}")

    # Mostra i primi byte del pacchetto (utile per debug)
    print(f"Dati grezzi (prime 20 byte): {raw_data[:20]}")

    # Lunghezza totale del pacchetto
    print(f"Lunghezza pacchetto: {len(raw_data)} byte")

    print("========================================\n")