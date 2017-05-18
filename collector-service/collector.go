package main

import (
	"fmt"
	"log"
	"net/http"
	"os"
	"time"

	"github.com/streadway/amqp"
)

var (
	rabbitURL      = "localhost:5672"
	rabbitUser     = "rabbit"
	rabbitPass     = "rabbit"
	rabbitExchange = "message"
	topic          = "survey.#"

	reconnectDelay = time.Second * 5

	conn *amqp.Connection
	ch   *amqp.Channel
)

func main() {

	if v := os.Getenv("TOPIC"); len(v) > 0 {
		topic = v
	}

	// Define a channel to receive rabbit close/shutdown events
	closeWatcher := make(chan *amqp.Error)

	var err error

	for conn == nil {
		conn, ch, err = connect()
		if err != nil {
			log.Printf("Failed to connect to rabbit: %v", err)
			time.Sleep(time.Second * 5)
		}
	}

	log.Printf("Listening on queue topic: %s", topic)

	conn.NotifyClose(closeWatcher)

	// TODO where should these actually close? What about after reconnects?
	defer conn.Close()
	defer ch.Close()

	// Close watcher implementation
	go func() {
		for rabbitErr := range closeWatcher {
			if conn != nil {
				ch.Close()
				conn.Close()
			}
			log.Printf("Received close event (%v) - attempt to reconnect in %s", rabbitErr, reconnectDelay)
			time.Sleep(reconnectDelay)
			log.Println("Reconnecting")

			// for conn == nil {
			for {
				conn, ch, err = connect()
				if err == nil {
					break
				}
				log.Printf("Failed to connect to rabbit: %v", err)
				time.Sleep(time.Second * 5)

			}
			// }
		}
	}()

	http.HandleFunc("/healthcheck", HealthcheckHandler)
	http.ListenAndServe(":8080", nil)
}

func HealthcheckHandler(rw http.ResponseWriter, r *http.Request) {
	rw.WriteHeader(http.StatusOK)
}

func connect() (*amqp.Connection, *amqp.Channel, error) {

	log.Println("Attempting to connect to rabbit")

	conn, err := amqp.Dial(fmt.Sprintf("amqp://%s:%s@%s", rabbitUser, rabbitPass, rabbitURL))
	if err != nil {
		return nil, nil, err
	}

	ch, err := conn.Channel()
	if err != nil {
		return nil, nil, err
	}

	err = ch.ExchangeDeclare(
		rabbitExchange, // name
		"topic",        // type
		true,           // durable
		false,          // auto delete
		false,          // internal
		false,          // no-wait
		nil,            // arguments
	)
	if err != nil {
		return nil, nil, err
	}

	q, err := ch.QueueDeclare(
		"",    // name
		false, // durable
		false, // delete when unused
		true,  // exclusive
		false, // no wait
		nil,   // arguments
	)
	if err != nil {
		return nil, nil, err
	}

	err = ch.QueueBind(
		q.Name,         // queue name
		topic,          // routing key
		rabbitExchange, // exchange
		false,
		nil,
	)
	if err != nil {
		return nil, nil, err
	}

	msgs, err := ch.Consume(
		q.Name, // queue
		"",     // consumer
		true,   // auto-ack
		false,  // exclusive
		false,  // no-local
		false,  // no-wait
		nil,    // arguments
	)
	if err != nil {
		return nil, nil, err
	}

	// TODO look into separating this out - maybe use contexts to ensure
	// go rountines correctly get destroyed on re-connect?
	go func() {
		for d := range msgs {
			log.Printf("Received a message: %s", d.Body)
		}
	}()
	log.Println("Waiting for messages")

	// 		conn.NotifyClose(watcher)

	return conn, ch, nil
}
