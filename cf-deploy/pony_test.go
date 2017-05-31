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

	// Must use the url supplied by the test server or we will be unable to
	// parse the parameters from it.
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
		// Again ensure the url is built using the base url from the test server
		// so that parameters are correctly captured.
		url := ts.URL + "/pony/" + pony
		resp, err := http.Get(url)
		if err != nil {
			t.Fatal(err)
		}

		body, err := ioutil.ReadAll(resp.Body)
		if err != nil {
			t.Fatal(err)
		}

		// TODO Test returned json - can't just string match as can't guarantee
		// marshalled order of elements.

		if string(body) != expected {
			t.Errorf("handler returned unexpected body for %s: got %s want %s", pony, body, expected)
		}
		resp.Body.Close()
	}
}
