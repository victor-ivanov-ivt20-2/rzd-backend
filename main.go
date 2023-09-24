package main

import (
	"backend/internal/ai"
	"backend/internal/config"
	"context"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"path/filepath"

	"github.com/gin-contrib/cors"
	"github.com/gin-gonic/gin"
)

type videos struct {
	id                  int
	train_id            int
	name                string
	date                string
	video_path          string
	all_activities_path string
	bad_activities_path string
	created_at          string
	deleted_at          string
}

type train struct {
	id   int
	name string
}

func main() {
	fmt.Println(config.GetEnvVar("PORT"))
	setupAPI(context.Background())
}

func startStream(c *gin.Context) {
	err := ai.ExecAI("./ai", "Python311/python.exe", "main.py", "start")
	if err != nil {
		log.Fatal(err)
	}
	c.IndentedJSON(http.StatusOK, "Началось")
}

func setupAPI(ctx context.Context) {
	router := gin.Default()

	router.Use(cors.Default())

	router.GET("/start-stream", startStream)

	router.POST("/upload", func(c *gin.Context) {
		// Получаем файл из запроса
		file, header, err := c.Request.FormFile("video")
		if err != nil {
			c.String(http.StatusBadRequest, "Bad request")
			return
		}
		defer file.Close()

		// Создаем папки для сохранения файла
		dir1 := "./ai/input/"
		if _, err := os.Stat(dir1); os.IsNotExist(err) {
			os.MkdirAll(dir1, os.ModePerm)
		}
		dir2 := "./src/renderer/public/"
		if _, err := os.Stat(dir2); os.IsNotExist(err) {
			os.MkdirAll(dir2, os.ModePerm)
		}

		// Создаем файлы на сервере
		filename := header.Filename
		out1, err := os.Create(filepath.Join(dir1, filename))
		if err != nil {
			c.String(http.StatusInternalServerError, "Error while creating the file")
			return
		}
		defer out1.Close()
		out2, err := os.Create(filepath.Join(dir2, filename))
		if err != nil {
			c.String(http.StatusInternalServerError, "Error while creating the file")
			return
		}
		defer out2.Close()

		// Копируем содержимое файла в созданные файлы
		_, err = io.Copy(out1, file)
		if err != nil {
			c.String(http.StatusInternalServerError, "Error while copying the file")
			return
		}
		_, err = file.Seek(0, 0)
		if err != nil {
			c.String(http.StatusInternalServerError, "Error while seeking the file")
			return
		}
		_, err = io.Copy(out2, file)
		if err != nil {
			c.String(http.StatusInternalServerError, "Error while copying the file")
			return
		}

		err = ai.ExecAI("./ai", "Python311/python.exe", "main.py", "input/"+filename)
		if err != nil {
			log.Fatal(err)
		}

		c.String(http.StatusOK, fmt.Sprintf("./"+filename))
	})

	router.Run("localhost:" + config.GetEnvVar("PORT"))
}
