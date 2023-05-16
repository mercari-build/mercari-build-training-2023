package main

import (
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"github.com/labstack/echo/v4"
	"github.com/labstack/echo/v4/middleware"
	"github.com/labstack/gommon/log"
	"io/ioutil"
	"mercari-build-training-2023/db"
	"net/http"
	"os"
	"path"
	"strconv"
	"strings"
)

const (
	ImgDir = "images"
	dbType = "sqlite3"
	dbPath = "mercari.sqlite3"
)

type Response struct {
	Message string `json:"message"`
}

func root(c echo.Context) error {
	res := Response{Message: "Hello, world!"}
	return c.JSON(http.StatusOK, res)
}

func addItem(c echo.Context) error {
	database, err := db.OpenDb(dbType, dbPath)
	if err != nil {
		fmt.Printf("error opening database: %v\n", err)
		return err
	}
	defer database.Close()
	// read the SQL file
	itemSql, err := os.Open("db/items.db")
	if err != nil {
		fmt.Printf("error opening SQL file: %v\n", err)
		return err
	}
	defer itemSql.Close()
	// read the content
	sqlBytes, err := ioutil.ReadAll(itemSql)
	if err != nil {
		fmt.Printf("error reading SQL file: %v\n", err)
		return err
	}
	_, err = database.Exec(string(sqlBytes))
	if err != nil {
		fmt.Printf("error executing SQL statements: %v\n", err)
		return err
	} else {
		fmt.Println("successfully execute SQL statements!")
	}

	// Get form data
	name := c.FormValue("name")
	c.Logger().Infof("Receive item: %s", name)
	category := c.FormValue("category")
	imgFile, err := c.FormFile("image")
	var imgFileName string
	if err != nil {
		fmt.Printf("error opening image file: %v\n", err)
		return err
	}
	// open the image file
	imgData, err := imgFile.Open()
	if err != nil {
		fmt.Printf("error reading image file: %v\n", err)
		return err
	}
	defer imgData.Close()

	bytes, err := ioutil.ReadAll(imgData)
	if err != nil {
		fmt.Printf("error reading image data: %v\n", err)
		return err
	}
	// sha256
	ShaInstance := sha256.New()
	ShaInstance.Write([]byte(bytes))
	shaRes := ShaInstance.Sum(nil)
	fmt.Printf("%x\n\n", shaRes)
	imgFileName = hex.EncodeToString(shaRes) + ".jpg"

	// save the image file with hashed name
	os.WriteFile(imgFileName, bytes, 0666)

	itemData := &db.ItemInfo{
		Name:          name,
		CategoryName:  category,
		ImageFilename: imgFileName,
	}

	// add item
	err = db.AddItemToDb(itemData, database)
	if err != nil {
		fmt.Printf("error adding item to db: %v\n", err)
		return err
	}

	message := fmt.Sprintf("item received: %s", name)
	res := Response{Message: message}
	return c.JSON(http.StatusOK, res)
}

func getItems(c echo.Context) error {
	database, err := db.OpenDb(dbType, dbPath)
	if err != nil {
		fmt.Printf("error opening database: %v\n", err)
		return err
	}
	defer database.Close()
	itemList, err := db.GetAllItems(database)
	if err != nil {
		fmt.Printf("error getting items: %v\n", err)
		return err
	}
	return c.JSON(http.StatusOK, itemList)
}

func searchItems(c echo.Context) error {
	// open the database
	database, err := db.OpenDb(dbType, dbPath)
	if err != nil {
		fmt.Printf("error opening database: %v\n", err)
		return err
	}
	defer database.Close()
	// get the query parameters
	key := c.QueryParam("keyword")
	items, err := db.SearchItems(key, database)
	if err != nil {
		fmt.Printf("error searching for items: %v\n", err)
		return err
	}
	return c.JSON(http.StatusOK, items)
}

func getItemsDetail(c echo.Context) error {
	itemId := c.Param("itemId")
	// string to int
	id, err := strconv.Atoi(itemId)
	if err != nil {
		fmt.Printf("error converting itemId to int: %v\n", err)
		return err
	}
	// database operation
	database, err := db.OpenDb(dbType, dbPath)
	if err != nil {
		fmt.Printf("error opening database: %v\n", err)
		return err
	}
	defer database.Close()

	item, err := db.GetItemById(id, database)
	if err != nil {
		fmt.Printf("error getting item by id: %v\n", err)
		return err
	}
	return c.JSON(http.StatusOK, item)
}

func getImg(c echo.Context) error {
	// Create image path
	imgPath := path.Join(ImgDir, c.Param("imageFilename"))

	if !strings.HasSuffix(imgPath, ".jpg") {
		res := Response{Message: "Image path does not end with .jpg"}
		return c.JSON(http.StatusBadRequest, res)
	}
	if _, err := os.Stat(imgPath); err != nil {
		fmt.Println(c.Logger().Level()) // 2 "INFO"
		c.Logger().SetLevel(log.DEBUG)  // set level to 1 or "DEBUG"
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

	e.GET("/items", getItems)

	e.GET("/items/:itemId", getItemsDetail)

	e.POST("/items", addItem)

	e.GET("/image/:imageFilename", getImg)

	e.GET("/search", searchItems)

	// Start server
	e.Logger.Fatal(e.Start(":9000"))
}
