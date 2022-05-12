"""
    API permettant de gérer les actions de l'objet connecté GW_CLOCK.
    @author Christopher Boisvert
    @created 2022-05-11
    @website https://greenwoodmultimedia.com
    @version 1.0.0
"""

from http.client import BAD_REQUEST
from flask import Flask
from flask_restful import Resource, Api
from flask import request
import sqlite3

"""
    Variables globales.
"""
app = Flask(__name__)
api = Api(app)
nom_bd = "db.db"
sqlite_utils = None

class SqliteUtils():
    """
        Classe utilitaire agissant comme interface entre Sqlite3 et mon Api.
    """

    #Objet contenant le pointeur vers la base de données.
    con = None

    def __init__(self, nom_fichier):
        """
            Classe utilitaire agissant comme interface entre Sqlite3 et mon Api.
            @param 'nom_fichier' Nom de la base de données.
        """
        self.con = sqlite3.connect(f'file:{nom_fichier}?mode=rw', uri=True)
        self.con.row_factory = sqlite3.Row
        self.con.execute("PRAGMA foreign_keys = ON")

    def __del__(self):
        """
            Destructeur.
            S'assure que la base de données est fermé.
        """
        if self.con != None:
            self.con.close()

    def select(self, sql, params = None) -> list:
        """
            Fonction qui permet d'aller sélectionner des objets dans la bdd.
            @param 'sql' Code SQL à exécuter.
            @param 'params' Tuple contenant les paramètres.
            @return Objet de type 'List'.
        """
        cur = self.con.cursor()
        if params != None:
            new_cur = cur.execute(sql, params)
        else:
            new_cur = cur.execute(sql)
        self.con.commit()
        return [dict(ix) for ix in new_cur.fetchall()]

    def insert(self, sql, params) -> int:
        """
            Fonction qui permet d'aller insérer des objets dans la bdd.
            @param 'sql' Code SQL à exécuter.
            @param 'params' Tuple contenant les paramètres.
            @return Retourne le nombre de ligne insérer.
        """
        cur = self.con.cursor()
        new_cur = cur.execute(sql, params)
        self.con.commit()
        return new_cur.rowcount

    def update(self, sql, params) -> int:
        """
            Fonction qui permet de mettre à jour les objets dans la base de données.
            @param 'sql' Code SQL à exécuter.
            @param 'params' Tuple contenant les paramètres.
            @return Retourne le nombre de ligne modifié.
        """
        cur = self.con.cursor()
        new_cur = cur.execute(sql, params)
        self.con.commit()
        return new_cur.rowcount

    def delete(self, sql, params) -> int:
        """
            Fonction qui permet de supprimer les objets dans la base de données.
            @param 'sql' Code SQL à exécuter.
            @param 'params' Tuple contenant les paramètres.
            @return Retourne le nombre de ligne supprimé.
        """
        cur = self.con.cursor()
        new_cur = cur.execute(sql, params)
        self.con.commit()
        return new_cur.rowcount
 
class Actions(Resource):
    """
        Classe représentant les routes CRUD pour l'objet action. Utilise l'objet 'Resource' de flask.
    """

    def get(self):
        """
            Méthode de type GET de la route /actions.
        """

        try:
            #On va chercher la base de données
            sqlite_utils = SqliteUtils(nom_bd)

            #Requête SQL
            sql = "SELECT id, date_time, value, est_effectue, type_action_id FROM actions"

            #Exécution de la requête
            resultats = sqlite_utils.select(sql)

            if resultats:
                return {"message":"Nous avons trouvés des actions.", "liste_actions": resultats}, 200

            else:
                return {"erreur":"Aucune action n'a été trouvé."}, 404

        except sqlite3.OperationalError as e:
            print("Erreur:" + str(e))
            return {"erreur":"Une erreur innattendue est survenue."}, 500

        except Exception as e:
            print("Erreur:" + str(e))
            return {"erreur":"Une erreur innattendue est survenue lors de l'obtention des actions"}, 500

    def post(self):
        """
            Méthode de type POST de la route /actions.
        """

        try:
            #On va chercher la base de données
            sqlite_utils = SqliteUtils(nom_bd)

            #On va chercher les données dans le body
            date_time = request.json["date_time"]
            value = request.json["value"]
            type_action_id = request.json["type_action_id"]

            if date_time == "":
                raise KeyError("Le champ date_time ne peut être vide.")
            if value == "":
                raise KeyError("Le champ value ne peut être vide.")
            if type_action_id == "":
                raise KeyError("Le champ type_action_id ne peut être vide.")
            if int(type_action_id) <= 0:
                raise KeyError("Le champ type_action_id ne peut être zéro ou négatif.")

            sql = "INSERT INTO actions(date_time, value, est_effectue, type_action_id) values (?,?,0,?)"

            #On va enregistrer les données dans la bdd
            nombre_ligne_ajoute = sqlite_utils.insert(sql, (date_time, value, type_action_id))

            if nombre_ligne_ajoute > 0:
                return {"message":"Nous avons bien enregistré l'action."}, 200

            else:
                return {"erreur":"Une erreur innattendue est survenue lors de l'enregistrement de l'action."}

        except KeyError as e:
            print("Erreur:" + str(e))
            error = str(e).replace("'","")
            return {"erreur":"Une erreur existe dans un de champs.", "description": error}, 400

        except sqlite3.OperationalError as e:
            print("Erreur:" + str(e))
            error = str(e).replace("'","")
            return {"erreur":"Une erreur innattendue est survenue."}, 500

        except Exception as e:
            print("Erreur:" + str(e))
            return {"erreur":"Une erreur innattendue est survenue."}, 500

    def patch(self):
        """
            Méthode de type PATCH de la route /actions.
        """

        try:
            #On va chercher la base de données
            sqlite_utils = SqliteUtils(nom_bd)

            #On va chercher les données dans le body
            id = request.json["id"]
            date_time = request.json["date_time"]
            value = request.json["value"]
            est_effectue = request.json["est_effectue"]
            type_action_id = request.json["type_action_id"]

            if id == "":
                raise KeyError("Le champ id ne peut être vide.")
            if int(id) <= 0:
                raise KeyError("Le champ id ne peut être zéro ou négatif.")
            if date_time == "":
                raise KeyError("Le champ date_time ne peut être vide.")
            if value == "":
                raise KeyError("Le champ value ne peut être vide.")
            if est_effectue == "":
                raise KeyError("Le champ id ne peut être vide.")
            if int(est_effectue) <= 0:
                raise KeyError("Le champ id ne peut être zéro ou négatif.")
            if type_action_id == "":
                raise KeyError("Le champ type_action_id ne peut être vide.")
            if int(type_action_id) <= 0:
                raise KeyError("Le champ type_action_id ne peut être zéro ou négatif.")

            sql = "UPDATE actions SET date_time=?, value=?, est_effectue=?, type_action_id=? WHERE id=?"

            #On va enregistrer les données dans la bdd
            nombre_ligne_ajoute = sqlite_utils.insert(sql, (date_time, value, est_effectue, type_action_id, id))

            #Si plus d'une ligne est modifié, ca veut dire que tout est beau
            if nombre_ligne_ajoute > 0:
                return {"message":"Nous avons bien modifié l'action."}, 200

            #Sinon, on retourne un message d'erreur
            else:
                return {"erreur":"L'action n'a pas pu être modifié, car celle-ci n'existe pas."}, 404

        except KeyError as e:
            print("Erreur:" + str(e))
            error = str(e).replace("'","")
            return {"erreur":"Une erreur existe dans un de champs.", "description": error}, 400

        except sqlite3.OperationalError as e:
            print("Erreur:" + str(e))
            error = str(e).replace("'","")
            return {"erreur":"Une erreur innattendue est survenue."}, 500

        except Exception as e:
            print("Erreur:" + str(e))
            return {"erreur":"Une erreur innattendue est survenue."}, 500

    def delete(self):
        """
            Méthode de type DELETE de la route /actions.
        """

        try:
            #On va chercher la base de données
            sqlite_utils = SqliteUtils(nom_bd)

            #On va chercher les données dans le body
            id = request.json["id"]

            if id == "":
                raise KeyError("Le champ id ne peut être vide.")
            if int(id) <= 0:
                raise KeyError("Le champ id ne peut être zéro ou négatif.")

            sql = "DELETE FROM actions WHERE id=?"

            #On va enregistrer les données dans la bdd
            nombre_ligne_modifie = sqlite_utils.insert(sql, (id))

            if nombre_ligne_modifie > 0:
                return {"message":"Nous avons bien supprimé l'action."}, 200
                
            else:
                return {"erreur":"L'action n'a pas été trouvé et donc n'a pas été supprimé."}, 404

        except KeyError as e:
            print("Erreur:" + str(e))
            error = str(e).replace("'","")
            return {"erreur":"Une erreur existe dans un de champs.", "description": error}, 400

        except sqlite3.OperationalError as e:
            print("Erreur:" + str(e))
            error = str(e).replace("'","")
            return {"erreur":"Une erreur innattendue est survenue."}, 500

        except Exception as e:
            print("Erreur:" + str(e))
            return {"erreur":"Une erreur innattendue est survenue."}, 500


class ActionsCompleter(Resource):
    """
        Classe représentant la route pour compléter les objets actions. Utilise l'objet 'Resource' de flask.
    """

    def post(self):
        """
            Fonction qui répond au requête Flask de type post sur la route /action/completer.
        """
        try:
            #On va chercher la base de données
            sqlite_utils = SqliteUtils(nom_bd)

            #On va chercher les données dans le body
            id = request.json["id"]

            #Validation de ID
            if id == "":
                raise KeyError("Le champ id ne peut être vide.")
            if int(id) <= 0:
                raise KeyError("Le champ id ne peut être zéro ou négatif.")

            #Requête SQL
            sql = "UPDATE actions SET est_effectue=1 WHERE id=?"

            #On va enregistrer les données dans la bdd
            nombre_ligne_modifie = sqlite_utils.insert(sql, (id))

            #Si une ligne a été effectivement modifié, on retourne une réponse positive
            if nombre_ligne_modifie > 0:
                return {"message":"Nous avons bien modifié l'action."}, 200

            #Sinon, on retourne une réponse négative
            else:
                return {"erreur":"Une erreur innattendue est survenue lors de la modification de l'action."}

        except KeyError as e:
            print("Erreur:" + str(e))
            error = str(e).replace("'","")
            return {"erreur":"Une erreur existe dans un de champs.", "description": error}, 400

        except sqlite3.OperationalError as e:
            print("Erreur:" + str(e))
            error = str(e).replace("'","")
            return {"erreur":"Une erreur innattendue est survenue."}, 500

        except Exception as e:
            print("Erreur:" + str(e))
            return {"erreur":"Une erreur innattendue est survenue."}, 500


"""
    Routes liés au serveur
"""
api.add_resource(Actions, '/actions')
api.add_resource(ActionsCompleter, "/actions/completer")
 
"""
    Point de lancement du serveur
"""
if __name__ == '__main__':
    try:
        print("Lancement du serveur...")
        app.run()
    except Exception as e:
        print(e)