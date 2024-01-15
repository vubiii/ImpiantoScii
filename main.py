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
        print("Difficoltà percorso")


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
