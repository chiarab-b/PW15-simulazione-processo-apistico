"""
Project Work 15 - Simulazione di un processo produttivo nel settore primario

Caso di studio:
azienda apistica (miele, propoli, cera d'api)

Le rese di prodotto sono basate su dati reali di settore (Osservatorio
Nazionale Miele, Regione Piemonte - IPLA S.p.A., Coldiretti):

- miele: 15-20 kg/alveare in un'annata ordinaria
- propoli: 50-70 g/alveare
- cera: 1-2% del peso del miele raccolto (è un sottoprodotto della smielatura)

I tempi di lavorazione per kg, invece, sono stime plausibili: non ho trovato
fonti ufficiali su questo aspetto specifico.
"""

import random

# ------------------------------------------------------------------
# Configurazione dell'apiario
# ------------------------------------------------------------------

NUMERO_ARNIE = 18

# rese medie per arnia

RESA_MIELE_MIN_KG = 15
RESA_MIELE_MAX_KG = 20

RESA_PROPOLI_MIN_KG = 0.05
RESA_PROPOLI_MAX_KG = 0.07

PERCENTUALE_CERA_MIN = 0.01
PERCENTUALE_CERA_MAX = 0.02

# tempo per kg e capacità giornaliera per ciascun prodotto (modificabili
# tramite le funzioni più sotto)

CONFIGURAZIONE_PROCESSO = {
    "miele": {
        "tempo_per_kg": 6, # centrifugazione, tempi rapidi
        "capacita_giornaliera": 40,
    },

    "propoli": {
        "tempo_per_kg": 480, # raccolta manuale, molto più lenta
        "capacita_giornaliera": 1.5,
    },

    "cera": {
        "tempo_per_kg": 15,
        "capacita_giornaliera": 6,
    },
}

CAPACITA_GIORNALIERA_COMPLESSIVA_MINUTI = 480 # 8 ore di lavoro


# ------------------------------------------------------------------
# Generazione casuale delle quantità
# ------------------------------------------------------------------

def genera_quantita_miele(numero_arnie):
    # quantità di miele raccolta nel lotto, in base alla resa per arnia
    resa_per_arnia = random.uniform(RESA_MIELE_MIN_KG, RESA_MIELE_MAX_KG)
    return round(resa_per_arnia * numero_arnie, 2)


def genera_quantita_propoli(numero_arnie):
    # stessa logica del miele, ma le quantità in gioco sono molto più piccole
    resa_per_arnia = random.uniform(RESA_PROPOLI_MIN_KG, RESA_PROPOLI_MAX_KG)
    return round(resa_per_arnia * numero_arnie, 2)


def genera_quantita_cera(quantita_miele):
    """
    A differenza di miele e propoli, la cera non viene raccolta in modo
    indipendente: è un sottoprodotto della smielatura, quindi la calcolo
    come percentuale della quantità di miele ottenuta.
    """
    percentuale = random.uniform(PERCENTUALE_CERA_MIN, PERCENTUALE_CERA_MAX)
    return round(quantita_miele * percentuale, 2)


# ------------------------------------------------------------------
# Configurazione del processo
# ------------------------------------------------------------------

def imposta_tempo_per_kg(prodotto, nuovo_tempo):
    CONFIGURAZIONE_PROCESSO[prodotto]["tempo_per_kg"] = nuovo_tempo


def imposta_capacita_giornaliera(prodotto, nuova_capacita):
    CONFIGURAZIONE_PROCESSO[prodotto]["capacita_giornaliera"] = nuova_capacita


def imposta_capacita_complessiva(nuova_capacita_minuti):
    # capacità giornaliera dell'intero apiario, non del singolo prodotto
    global CAPACITA_GIORNALIERA_COMPLESSIVA_MINUTI
    CAPACITA_GIORNALIERA_COMPLESSIVA_MINUTI = nuova_capacita_minuti


def verifica_capacita_complessiva_rispettata(tempo_totale_minuti):
    return tempo_totale_minuti <= CAPACITA_GIORNALIERA_COMPLESSIVA_MINUTI


def verifica_capacita_rispettata(prodotto, quantita):
    # se la quantità raccolta supera quanto si riesce a lavorare in un
    # giorno, il codice restituisce solo la parte lavorabile: il resto
    # richiederebbe un altro giorno di lavoro
    capacita_massima = CONFIGURAZIONE_PROCESSO[prodotto]["capacita_giornaliera"]
    if quantita > capacita_massima:
        return capacita_massima
    return quantita


# ------------------------------------------------------------------
# Tempo di produzione
# ------------------------------------------------------------------

def calcola_tempo_produzione(prodotto, quantita):
    tempo_per_kg = CONFIGURAZIONE_PROCESSO[prodotto]["tempo_per_kg"]
    return round(quantita * tempo_per_kg, 2)


# ------------------------------------------------------------------
# Le due sequenze produttive richieste dalla traccia
# ------------------------------------------------------------------

def simula_sequenza_smielatura(numero_arnie):
    # Sequenza 1: smielatura, produce solo miele
    print("\n=== Sequenza 1 - Smielatura ===")
    quantita_generata = genera_quantita_miele(numero_arnie)
    quantita_effettiva = verifica_capacita_rispettata("miele", quantita_generata)

    # tempo necessario per lavorare l'intero lotto generato
    tempo_lotto = calcola_tempo_produzione("miele", quantita_generata)
    # tempo necessario per la quantità lavorabile nella giornata
    tempo_produzione = calcola_tempo_produzione("miele", quantita_effettiva)

    print(f"- Miele raccolto nel lotto: {quantita_generata} kg")
    print(f"  Quantità lavorabile in giornata (capacità max): {quantita_effettiva} kg")
    print(f"  Tempo necessario per l'intero lotto: {tempo_lotto} minuti")
    print(f"  Tempo di produzione giornaliero: {tempo_produzione} minuti")

    if not verifica_capacita_complessiva_rispettata(tempo_produzione):
        print("Attenzione: il tempo richiesto supera la capacità "
              "giornaliera complessiva dell'apiario!")

    return {
        "miele": {
            "quantita_kg": quantita_effettiva,
            "tempo_minuti": tempo_produzione,
            "tempo_lotto_minuti": tempo_lotto
        }
    }, quantita_generata


def simula_sequenza_propoli_cera(numero_arnie, quantita_miele_lotto):
    # Sequenza 2: raccolta di propoli e cera. La cera dipende dal miele
    # raccolto nella sequenza precedente, quindi va passato come parametro
    print("\n=== Sequenza 2 - Raccolta propoli e cera ===")
    risultati = {}
    tempo_totale_sequenza = 0

    for prodotto, quantita_generata in [
        ("propoli", genera_quantita_propoli(numero_arnie)),
        ("cera", genera_quantita_cera(quantita_miele_lotto)),
    ]:
        quantita_effettiva = verifica_capacita_rispettata(prodotto, quantita_generata)

        # tempo necessario per lavorare l'intero lotto generato
        tempo_lotto = calcola_tempo_produzione(prodotto, quantita_generata)
        # tempo necessario per la quantità lavorabile nella giornata
        tempo_produzione = calcola_tempo_produzione(prodotto, quantita_effettiva)

        risultati[prodotto] = {
            "quantita_kg": quantita_effettiva,
            "tempo_minuti": tempo_produzione,
            "tempo_lotto_minuti": tempo_lotto,
        }
        tempo_totale_sequenza += tempo_produzione

        print(f"- {prodotto.capitalize()}:")
        print(f"  Quantità generata nel lotto: {quantita_generata} kg")
        print(f"  Quantità lavorabile in giornata (capacità max): {quantita_effettiva} kg")
        print(f"  Tempo necessario per l'intero lotto: {tempo_lotto} minuti")
        print(f"  Tempo di produzione giornaliero: {tempo_produzione} minuti")

    print(f"Tempo totale della produzione giornaliera nella sequenza: "
          f"{tempo_totale_sequenza} minuti")

    if not verifica_capacita_complessiva_rispettata(tempo_totale_sequenza):
        print("Attenzione: il tempo richiesto supera la capacità "
              "giornaliera complessiva dell'apiario!")

    return risultati


if __name__ == "__main__":
    risultati_sequenza1, quantita_miele_lotto = simula_sequenza_smielatura(NUMERO_ARNIE)
    risultati_sequenza2 = simula_sequenza_propoli_cera(NUMERO_ARNIE, quantita_miele_lotto)
