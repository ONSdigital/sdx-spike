package main

import (
	"fmt"
	"log"

	"github.com/streadway/amqp"
)

var (
	rabbitURL  = "localhost:5672"
	rabbitUser = "rabbit"
	rabbitPass = "rabbit"
)

var (
	rabbitExchange = "message"
)

func main() {

	conn, err := amqp.Dial(fmt.Sprintf("amqp://%s:%s@%s", rabbitUser, rabbitPass, rabbitURL))
	failOnError(err, "Failed to connect to rabbit")
	defer conn.Close()

	ch, err := conn.Channel()
	failOnError(err, "Failed to open channel")
	defer ch.Close()

	err = ch.ExchangeDeclare(
		rabbitExchange, // name
		"topic",        // type
		true,           // durable
		false,          // auto delete
		false,          // internal
		false,          // no-wait
		nil,            // arguments
	)
	failOnError(err, "Failed to declare exchange")

	q, err := ch.QueueDeclare(
		"",    // name
		false, // durable
		false, // delete when unused
		true,  // exclusive
		false, // no wait
		nil,   // arguments
	)
	failOnError(err, "Failed to declare queue")

	// Bind to a queue topic
	err = ch.QueueBind(
		q.Name,         // queue name
		"survey.#",     // routing key
		rabbitExchange, // exchange
		false,
		nil,
	)
	failOnError(err, "Failed to bind to queue")

	msgs, err := ch.Consume(
		q.Name, // queue
		"",     // consumer
		true,   // auto-ack
		false,  // exclusive
		false,  // no-local
		false,  // no-wait
		nil,    // arguments
	)
	failOnError(err, "Failed to register a consumer")

	forever := make(chan bool)

	go func() {
		for d := range msgs {
			log.Printf("Received a message: %s", d.Body)
		}
	}()

	log.Println("Waiting for messages")
	<-forever
}

// Temporarily handle errors in a heavy handed way
func failOnError(err error, msg string) {
	if err != nil {
		log.Fatalf("%s: %s", msg, err)
	}
}
