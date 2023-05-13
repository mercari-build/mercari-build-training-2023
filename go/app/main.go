package main

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	_ "io/ioutil"
	"net/http"
	"os"
	"path"
	"strconv"
	"strings"

	"github.com/labstack/echo/v4"
	"github.com/labstack/echo/v4/middleware"
	"github.com/labstack/gommon/log"
)

const (
	ImgDir = "images"
)

type Response struct {
	Message string `json:"message"`
}

type Item struct {
	Name     string `json:"name"`
	Category string `json:"category"`
	Image    string `json:"image_filename"`
}

type Json struct {
	Items []Item `json:"item"`
}

func root(c echo.Context) error {
	res := Response{Message: "Hello, world!"}
	return c.JSON(http.StatusOK, res)
}

func getItem(c echo.Context) error {
	res := getJsonfile("app/items.json")
	return c.JSON(http.StatusOK, res)
}

func getItemWithId(c echo.Context) error {
	idString := c.Param("id")
	id, _ := strconv.Atoi(idString)
	currentFile := getJsonfile("app/items.json")
	res := currentFile.Items[id-1]
	return c.JSON(http.StatusOK, res)
}

func updateFileJson(item Item) error {
	currentFile := getJsonfile("app/items.json")
	currentFile.Items = append(currentFile.Items, item)
	err := currentFile.creatNewJsonfile("app/items.json")
	return err
}

func getJsonfile(filename string) Json {
	var currentFile Json
	currentFileBytes, _ := os.ReadFile(filename)
	_ = json.Unmarshal(currentFileBytes, &currentFile)
	return currentFile
}

func (j Json) creatNewJsonfile(filename string) error {
	newFileBytes, _ := json.Marshal(j)
	err := os.WriteFile(filename, newFileBytes, 0644)
	return err
}

func addItem(c echo.Context) error {
	// Get form data
	name := c.FormValue("name")
	category := c.FormValue("category")
	imagePass := c.FormValue("image")
	imageFile, _ := os.ReadFile(imagePass)
	imageHash32bytes := sha256.Sum256(imageFile)
	image := hex.EncodeToString(imageHash32bytes[:]) + ".jpg"
	item := Item{Name: name, Category: category, Image: image}
	_ = updateFileJson(item)

	c.Logger().Infof("Receive item: %s", name)

	message := fmt.Sprintf("item received: %s", name)
	res := Response{Message: message}

	return c.JSON(http.StatusOK, res)
}

func getImg(c echo.Context) error {
	// Create image path
	imgPath := path.Join(ImgDir, c.Param("imageFilename"))

	if !strings.HasSuffix(imgPath, ".jpg") {
		res := Response{Message: "Image path does not end with .jpg"}
		return c.JSON(http.StatusBadRequest, res)
	}
	if _, err := os.Stat(imgPath); err != nil {
		c.Logger().Debugf("Image not found: %s", imgPath)
		imgPath = path.Join(ImgDir, "default.jpg")
	}
	return c.File(imgPath)
}

func main() {
	e := echo.New()

	// Middleware
	e.Use(middleware.Logger())
	e.Use(middleware.Recover())
	e.Logger.SetLevel(log.INFO)

	front_url := os.Getenv("FRONT_URL")
	if front_url == "" {
		front_url = "http://localhost:3000"
	}
	e.Use(middleware.CORSWithConfig(middleware.CORSConfig{
		AllowOrigins: []string{front_url},
		AllowMethods: []string{http.MethodGet, http.MethodPut, http.MethodPost, http.MethodDelete},
	}))

	// Routes
	e.GET("/", root)
	e.GET("/items", getItem)
	e.POST("/items", addItem)
	e.GET("/image/:imageFilename", getImg)
	e.GET("/items/:id", getItemWithId)

	// Start server
	e.Logger.Fatal(e.Start(":9000"))
}
