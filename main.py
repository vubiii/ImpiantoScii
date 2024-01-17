from neo4j import GraphDatabase
import traceback

class NeoManager:
    def __init__(self, neo4j_username, neo4j_password, neo4j_uri):
        self.neo4j_uri = neo4j_uri
        self.neo4j_username = neo4j_username
        self.neo4j_password = neo4j_password
        self.driver = None

    def apri_connessione(self):
        print(f"Connessione al database {self.neo4j_uri}.")
        try:
            self.driver = GraphDatabase.driver(
                self.neo4j_uri,
                auth=(self.neo4j_username, self.neo4j_password))
            print(f"Connessione al database {self.neo4j_uri} stabilita.")
        except Exception as e:
            print(f"Errore durante la connessione: {e}")
            traceback.print_exc()

    def chiudi_connessione(self):
        print("Chiusura della connessione al database.")
        if self.driver:
            self.driver.close()
            print("Connessione chiusa.")

    def stampa_path(self, path):
        nodes = path.nodes
        relationships = path.relationships
        lunghezza_totale = 0
        for i in range(len(relationships)):
            node = nodes[i]
            relationship = relationships[i]
            lunghezza_totale += relationship["lunghezza"]

        last_node = nodes[-1]
        print(f"Percorso più difficile: {last_node['pista']} ({last_node['colore']}), Lunghezza totale: {lunghezza_totale}")

    def difficolta_percorso(self):
        print("Trovo il percorso più facile su due impianti")
        print("Ecco gli impianti :")

        dizionario_scelta = {}
        impianti = self.trova_impianti()

        for i, impianto in enumerate(impianti):
            print(f"{i} - {impianto}")
            dizionario_scelta[i] = impianto

        scelta = int(input("Inserire la scelta:"))

        with self.driver.session() as session:
            impianto_inizio = dizionario_scelta[scelta]
            print("Cerco il percorso più facile")
            risultato = session.run(
                """
                MATCH (impianto:ImpiantoRisalita {nome: $impianto_inizio, tipo: "fine"})
                MATCH (impianto)-[:SERVE*]->(start:SegmentoPista {inizio: true})
                MATCH (end:SegmentoPista {fine: true, pista: start.pista})
                MATCH path = allShortestPaths((start)-[:SEGUITE_DA*]-(end))
                RETURN path;
                """,
                impianto_inizio=impianto_inizio,
            )

            for record in risultato:
                path = record["path"]
                self.calcola_difficolta_percorso(path)

    def calcola_difficolta_percorso(self, path):
        somma_difficolta = 0
        min_difficulty = float('inf')  
        min_difficulty_pista = None

        for rel in path.relationships:
            difficoltà_rel = rel["difficolta"]
            if difficoltà_rel == "facile":
                somma_difficolta += 0
            elif difficoltà_rel == "media":
                somma_difficolta += 1
            elif difficoltà_rel == "difficile":
                somma_difficolta += 2

            pista = rel["pista"]
            #print(f"Segmento Pista: {pista}, Difficoltà: {difficoltà_rel}")

            if somma_difficolta < min_difficulty:
                min_difficulty = somma_difficolta
                min_difficulty_pista = pista

        # Stampa solo la pista con difficoltà minima
        print("Pista con la difficoltà minima:", min_difficulty_pista)

    def visualizza_piste(self):
        with self.driver.session() as session:
            # Per vedere tutte le piste
            risultato = session.run("MATCH (n:SegmentoPista) RETURN DISTINCT n.pista AS nome_pista;")
            piste_totali = [record["nome_pista"] for record in risultato]
            return piste_totali

    def piste_aperte(self):
        with self.driver.session() as session:
            print("Cerco le piste aperte")
            risultato = session.run("MATCH (n:SegmentoPista)-[r:SEGUITE_DA]->(m) WHERE r.stato = 0 RETURN DISTINCT r.pista AS nome_pista;")
            piste_chiuse = [record["nome_pista"] for record in risultato]
            #print(f"\nLe piste chiuse sono: {', '.join(piste_chiuse)}")
            # Commentato

            piste_totali = self.visualizza_piste()

            piste_aperte = [pista for pista in piste_totali if pista not in piste_chiuse]
            print(f"Le piste aperte sono: {', '.join(piste_aperte)}")

    def visualizza_piste_colore(self):
        dizionario_colori = {"verde": 0, "blu": 1, "rossa": 2, "nera": 3}
        dizionario_colori_inverso = {0: "verde",1: "blu",  2: "rossa",  3:"nera"}
        piste_ordine = []

        with self.driver.session() as session:
            risultato = session.run("MATCH (n:SegmentoPista) RETURN DISTINCT n.pista, n.colore;")
            piste = [record.values() for record in risultato]

            # Ordina la lista piste in base ai valori del dizionario_colori
            piste_ordinate = sorted(piste, key=lambda x: dizionario_colori.get(x[1], float('inf')))

            for pista in piste_ordinate:
                nome_pista, colore = pista
                valore_pista = dizionario_colori[colore]
                piste_ordine.append((nome_pista, valore_pista))

            # Stampa ordinata
            print("Piste ordinate per colore:")
            for pista in piste_ordine:
                print(f"- Pista: {pista[0]}, {dizionario_colori_inverso.get(pista[1])}")

            return piste_ordine
        
    def trova_impianti(self):
        with self.driver.session() as session:
            risultato = session.run("MATCH (n:ImpiantoRisalita) RETURN DISTINCT n.nome")
            impianti = [record["n.nome"] for record in risultato]
            return impianti

    def percorso_breve(self):
        print("Trova il percorso più breve su gli impianti di risalita")
        print("Ecco gli impianti :")
        
        dizionario_scelta = {}
        impianti = self.trova_impianti()

        for i, impianto in enumerate(impianti):
            print(f"{i} - {impianto}")
            dizionario_scelta[i] = impianto

        scelta = int(input("Inserire la scelta:"))

        with self.driver.session() as session:
            print("Cerco il percorso più breve")
            impianto_inizio = dizionario_scelta[scelta]
            risultato = session.run(
                f"""
                MATCH (start:ImpiantoRisalita {{nome: "{impianto_inizio}", tipo: "inizio"}})
                MATCH (end:ImpiantoRisalita {{nome: "{impianto_inizio}", tipo: "fine"}})
                
                MATCH path = shortestPath((start)-[*..10]-(end))
                WHERE ALL(rel IN relationships(path) WHERE TYPE(rel) <> 'Risalita')
                RETURN nodes(path) AS nodi, length(path) AS lunghezzaTotale
                ORDER BY lunghezzaTotale
                LIMIT 1;
                """
            )

            record = risultato.single()
            if record:
                percorso = record["nodi"]
                lunghezza_totale = record["lunghezzaTotale"]
                segmento_pista_node = next((node for node in percorso if "SegmentoPista" in node.labels), None)
                if segmento_pista_node:
                    print(f"Nome: {segmento_pista_node['pista']}, Colore: {segmento_pista_node['colore']}")
            else:
                print("Nessun percorso più breve trovato.")



def interfaccia_utente(neo_manager):
    while True:
        print("\n--- SCII APP ---")
        print("1 - Visualizza le piste aperte") # DONE
        print("2 - Visualizza il percorso più breve collegato da un impianto") # DONE
        print("3 - Visualizza il percorso più facile collegato da un impianto") # DONE
        print("4 - Visualizza le piste in ordine di difficoltà") # DONE
        print("0 - Esci")
        print("-----------------")

        try:
            scelta = int(input("Inserire la scelta: "))
            if scelta == 0:
                print("Arrivederci!")
                break
            elif scelta == 1:
                neo_manager.piste_aperte()
            elif scelta == 2:
                neo_manager.percorso_breve()
            elif scelta == 3:
                neo_manager.difficolta_percorso()
            elif scelta == 4:
                neo_manager.visualizza_piste_colore()
            else:
                print("Scelta non valida. Riprova.")
        except ValueError:
            print("Inserire un numero valido.")
        except Exception as e:
            print(f"Si è verificato un errore: {e}")


if __name__ == "__main__":
    neo_manager = NeoManager(neo4j_username="neo4j", neo4j_password="Es@meneo4!", neo4j_uri="bolt+s://0d076a41.databases.neo4j.io:7687")

    try:
        neo_manager.apri_connessione()
        interfaccia_utente(neo_manager)
    except Exception as e:
        print(f"Errore durante l'esecuzione delle operazioni: {e}")
        traceback.print_exc()
    finally:
        neo_manager.chiudi_connessione()
