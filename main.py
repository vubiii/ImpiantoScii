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

    def visualizza_piste(self):
        pass

    def piste_aperte(self):
        with self.driver.session() as session:
            print("Cerco le piste aperte")
            risultato = session.run("MATCH (n)-[r:SEGUITE_DA]->(m) WHERE r.stato = 0 RETURN DISTINCT r.pista AS nome_pista;")
            piste_chiuse = [record["nome_pista"] for record in risultato]
            print(f"Le piste chiuse sono {piste_chiuse}")

            piste = self.visualizza_piste()
            piste_totali = [pista[0] for pista in piste]

            piste_aperte = [pista for pista in piste_totali if pista not in piste_chiuse]
            print(f"Le piste aperte sono {piste_aperte}")

    def percorso_breve(self):
        pass

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
            print(f"Segmento Pista: {pista}, Difficoltà: {difficoltà_rel}")

         
            if somma_difficolta < min_difficulty:
                min_difficulty = somma_difficolta
                min_difficulty_pista = pista

        print("Pista con la difficoltà minima:", min_difficulty_pista)


if __name__ == "__main__":
    # Esempio di utilizzo della classe NeoManager
    neo_manager = NeoManager(neo4j_username="neo4j", neo4j_password="Es@meneo4!", neo4j_uri="bolt+s://0d076a41.databases.neo4j.io:7687")
    
    try:
        neo_manager.apri_connessione()
        # Esegui le operazioni sul database
        # neo_manager.crea_nodi()
        # neo_manager.crea_collegamenti()
        neo_manager.visualizza_piste()
        neo_manager.piste_aperte()
        neo_manager.percorso_breve()
        neo_manager.difficolta_percorso()
    except Exception as e:
        print(f"Errore durante l'esecuzione delle operazioni: {e}")
        traceback.print_exc()
    finally:
        neo_manager.chiudi_connessione()
