package main

import (
	"io/ioutil"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/gorilla/mux"
)

func TestPonyList(t *testing.T) {
	// Create a new router and plug in the defined routes
	r := mux.NewRouter()
	setUpRoutes(r)

	ts := httptest.NewServer(r)
	defer ts.Close()

	url := ts.URL + "/pony"
	resp, err := http.Get(url)
	if err != nil {
		t.Fatal(err)
	}

	if resp.StatusCode != http.StatusOK {
		t.Errorf("bad status code, got %v want %v", resp.StatusCode, http.StatusOK)
	}

}

func TestPony(t *testing.T) {

	// Create a new router and plug in the defined routes
	r := mux.NewRouter()
	setUpRoutes(r)

	ts := httptest.NewServer(r)
	defer ts.Close()

	// fmt.Println(string(body))

	cases := map[string]string{
		"fluttershy":      `{"name":"fluttershy","element":"kindness"}`,
		"pinkiepie":       `{"name":"pinkiepie","element":"laughter"}`,
		"rainbowdash":     `{"name":"rainbowdash","element":"loyalty"}`,
		"rarity":          `{"name":"rarity","element":"generosity"}`,
		"twilightsparkle": `{"name":"twilightsparkle","element":"magic"}`,
		"applejack":       `{"name":"applejack","element":"honesty"}`,
		"nopony":          `{"name":"discord","element":"chaos!"}`,
	}

	for pony, expected := range cases {
		url := ts.URL + "/pony/" + pony
		resp, err := http.Get(url)
		if err != nil {
			t.Fatal(err)
		}

		body, err := ioutil.ReadAll(resp.Body)
		if err != nil {
			t.Fatal(err)
		}

		if string(body) != expected {
			t.Errorf("handler returned unexpected body for %s: got %s want %s", pony, body, expected)
		}
		resp.Body.Close()
	}
}
