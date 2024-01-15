from neo4j import GraphDatabase
import traceback

class NeoManager:
    def __init__(self, neo4j_username, neo4j_password, neo4j_uri):
        self.neo4j_uri = neo4j_uri
        self.neo4j_username = neo4j_username
        self.neo4j_password = neo4j_password
        self.driver = None

    def open(self):
        print(f"Collegandosi al database {self.neo4j_uri}.")
        self.driver = GraphDatabase.driver(
            self.neo4j_uri,
            auth=(self.neo4j_username, self.neo4j_password))
        print(f"Collegato al database {self.neo4j_uri}.")

    def close(self):
        print("Chiusura della connessione al database.")
        if self.driver:
            self.driver.close()
            print("Connessione chiusa.")

    def visualizza_piste(self):
        dizionario_colori = {"verde": 0, "blu": 1, "rossa": 2, "nera": 3}
        piste_ordine = []

        with self.driver.session() as session:
            risultato = session.run("MATCH (n:SegmentoPista) RETURN DISTINCT n.pista, n.colore;")
            piste = [record.values() for record in risultato]

            # Ordina la lista piste in base ai valori del dizionario_colori
            piste_ordinate = sorted(piste, key=lambda x: dizionario_colori.get(x[1], float('inf')))

            for pista in piste_ordinate:
                valore_pista = dizionario_colori[pista[1]]
                piste_ordine.append((pista[0], valore_pista))
                print(pista)

            return piste_ordine

    def piste_aperte(self):
        pass

    def percorso_breve(self):
        pass

    def difficolta_percorso(self):
        pass


if __name__ == "__main__":
    # Esempio di utilizzo della classe NeoManager
    neo_manager = NeoManager(neo4j_username="neo4j", neo4j_password="Es@meneo4!", neo4j_uri="bolt://0d076a41.databases.neo4j.io:7687/db.scii")
    
    try:
        neo_manager.open()
        # Esegui le operazioni sul database
        neo_manager.crea_nodi()
        neo_manager.crea_collegamenti()
        neo_manager.visualizza_piste()
        neo_manager.piste_aperte()
        neo_manager.percorso_breve()
        neo_manager.difficolta_percorso()
    except Exception as e:
        print(f"Errore durante l'esecuzione delle operazioni: {e}")
        traceback.print_exc()
    finally:
        neo_manager.close()
