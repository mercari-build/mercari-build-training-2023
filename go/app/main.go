package main

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"github.com/labstack/echo/v4"
	"github.com/labstack/echo/v4/middleware"
	"github.com/labstack/gommon/log"
	"io/ioutil"
	"net/http"
	"os"
	"path"
	"strconv"
	"strings"
)

const (
	ImgDir = "images"
)

type Response struct {
	Message string `json:"message"`
}

type ResponseItems struct {
	Items []ItemInfo `json:"items"`
}

type ItemInfo struct {
	Name          string `json:"name"`
	Category      string `json:"category"`
	ImageFilename string `json:"image_filename"`
}

func root(c echo.Context) error {
	res := Response{Message: "Hello, world!"}
	return c.JSON(http.StatusOK, res)
}

func addItem(c echo.Context) error {
	// Open and read items.json
	var jsonItems ResponseItems
	jsonFile, err := os.Open("items.json")
	if err != nil {
		fmt.Println("fail to open items.json")
	}
	defer jsonFile.Close()
	jsonData, err := ioutil.ReadAll(jsonFile)
	//convert []byte to json
	json.Unmarshal(jsonData, &jsonItems)

	// Get form data
	name := c.FormValue("name")
	c.Logger().Infof("Receive item: %s", name)
	category := c.FormValue("category")
	imgFile, err := c.FormFile("image")
	var imgFileName string
	if err != nil {
		fmt.Println("fail to open image file")
	} else {
		// open the image file
		imgData, err := imgFile.Open()

		if err != nil {
			fmt.Println("fail to read image file")
			return err
		}
		defer imgData.Close()

		bytes, _ := ioutil.ReadAll(imgData)

		// sha256
		ShaInstance := sha256.New()
		ShaInstance.Write([]byte(bytes))
		shaRes := ShaInstance.Sum(nil)
		fmt.Printf("%x\n\n", shaRes)
		imgFileName = hex.EncodeToString(shaRes) + ".jpg"

		// save the image file with hashed name
		os.WriteFile(imgFileName, bytes, 0666)
	}

	itemData := &ItemInfo{
		Name:          name,
		Category:      category,
		ImageFilename: imgFileName,
	}

	jsonItems.Items = append(jsonItems.Items, *itemData)

	// convert json to []byte and write it in json file
	data, _ := json.MarshalIndent(jsonItems, "", "\t")
	os.WriteFile("items.json", data, 0777)

	message := fmt.Sprintf("item received: %s", name)
	res := Response{Message: message}
	return c.JSON(http.StatusOK, res)
}

func getItems(c echo.Context) error {
	jsonFile, err := os.Open("items.json")
	if err != nil {
		fmt.Println("error opening json file")
		return err
	}

	defer jsonFile.Close()

	jsonData, err := ioutil.ReadAll(jsonFile)
	if err != nil {
		fmt.Println("fail to read json file")
		return err
	}

	var jsonContent ResponseItems
	json.Unmarshal(jsonData, &jsonContent)
	return c.JSON(http.StatusOK, jsonContent)

}

func getItemsDetail(c echo.Context) error {
	itemId := c.Param("itemId")
	// string to int
	id, err := strconv.Atoi(itemId)

	jsonFile, err := os.Open("items.json")
	if err != nil {
		fmt.Println("error opening json file")
		return err
	}
	defer jsonFile.Close()

	jsonData, err := ioutil.ReadAll(jsonFile)
	if err != nil {
		fmt.Println("fail to read json file")
		return err
	}

	var jsonContent ResponseItems
	json.Unmarshal(jsonData, &jsonContent)
	if id-1 >= 0 && id-1 < len(jsonContent.Items) {
		itemDetail := jsonContent.Items[id-1]
		return c.JSON(http.StatusOK, itemDetail)
	} else {
		message := Response{Message: "The item is not exist."}
		return c.JSON(http.StatusBadRequest, message)
	}
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

	// Start server
	e.Logger.Fatal(e.Start(":9000"))
}
