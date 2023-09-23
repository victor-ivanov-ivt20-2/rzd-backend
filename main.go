package main

import (
	"backend/internal/ai"
	"backend/internal/config"
	"context"
	"fmt"
	"log"
)

func main() {
	fmt.Println(config.GetEnvVar("PORT"))
	err := ai.ExecAI("./ai", "Python311/python.exe", "main.py", "123.png")
	if err != nil {
		log.Fatal(err)
	}
}

func setupAPI(ctx context.Context) {

}
