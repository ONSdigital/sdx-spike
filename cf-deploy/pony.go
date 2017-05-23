package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"

	"github.com/gorilla/mux"
)

var ponies = map[string]string{
	"applejack":       "honesty",
	"pinkiepie":       "laughter",
	"rarity":          "generosity",
	"rainbowdash":     "loyalty",
	"twilightsparkle": "magic",
	"fluttershy":      "kindness",
}

func main() {
	port := os.Getenv("PORT")
	if len(port) == 0 {
		log.Fatal("No PORT set")
	}

	r := mux.NewRouter()

	setUpRoutes(r)

	http.Handle("/", r)
	http.ListenAndServe(fmt.Sprintf(":%s", port), nil)
}

func setUpRoutes(r *mux.Router) {
	r.HandleFunc("/pony", handlePonyList).Methods("GET")
	r.HandleFunc("/pony/{name}", handlePony).Methods("GET")
}

type Pony struct {
	Name    string `json:"name"`
	Element string `json:"element"`
}

type PonyList struct {
	Ponies []Pony `json:"ponies"`
}

func handlePonyList(rw http.ResponseWriter, r *http.Request) {
	list := []Pony{}

	for k, v := range ponies {
		list = append(list, Pony{Name: k, Element: v})
	}

	pl := PonyList{Ponies: list}
	json, err := json.Marshal(&pl)
	if err != nil {
		rw.WriteHeader(http.StatusInternalServerError)
		rw.Write([]byte(`Bad pony marshalling`))
		return
	}

	rw.WriteHeader(http.StatusOK)
	rw.Header().Set("Content-type", "application/json")
	rw.Write(json)
}

func handlePony(rw http.ResponseWriter, r *http.Request) {

	vars := mux.Vars(r)

	pr := Pony{Name: "discord", Element: "chaos!"}
	name := vars["name"]

	if val, ok := ponies[name]; ok {
		pr.Element = val
		pr.Name = name
	}

	json, err := json.Marshal(&pr)
	if err != nil {
		rw.WriteHeader(http.StatusInternalServerError)
		rw.Write([]byte(`Bad pony marshalling`))
		return
	}

	rw.WriteHeader(http.StatusOK)
	rw.Header().Set("Content-type", "application/json")
	rw.Write(json)
}
