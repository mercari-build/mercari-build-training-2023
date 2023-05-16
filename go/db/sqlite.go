package db

import (
	"database/sql"
	"fmt"
	_ "github.com/mattn/go-sqlite3"
)

type ItemsList struct {
	Items []ItemInfo `json:"items"`
}

type ItemInfo struct {
	Name          string `json:"name"`
	CategoryName  string `json:"category_name"`
	ImageFilename string `json:"image_filename"`
}

func OpenDb(dbType string, filePath string) (db *sql.DB, err error) {
	db, err = sql.Open(dbType, filePath)
	if err != nil {
		fmt.Printf("error opening database file: %v\n", err)
	}
	return db, err
}

func AddItemToDb(item *ItemInfo, db *sql.DB) error {
	// QueryRow executes a query that is expected to return at most one row.
	rows := db.QueryRow("SELECT id FROM category WHERE name = ?", item.CategoryName)
	var categoryId int
	err := rows.Scan(&categoryId)
	// insert new category if doesn't exist
	if err != nil {
		r, e := db.Exec("INSERT INTO category(name) VALUES (?)", item.CategoryName)
		if e != nil {
			fmt.Printf("error inserting category name: %v\n", e)
			return e
		}
		id, _ := r.LastInsertId()
		categoryId = int(id)
	}
	res, err := db.Exec("INSERT INTO items(name, category_id, image_name) VALUES (?, ?, ?)", item.Name, categoryId, item.ImageFilename)
	if err != nil {
		fmt.Printf("error inserting data: %v\n", err)
		return err
	}
	// get the self-incrementing id
	lastInsertId, err := res.LastInsertId()
	if err != nil {
		fmt.Printf("error getting last insert id: %v\n", err)
		return err
	}
	fmt.Printf("last insert id: %d\n", lastInsertId)
	return nil
}

func GetAllItems(db *sql.DB) (r *ItemsList, e error) {
	rows, err := db.Query("SELECT items.name, category.name, image_name FROM items INNER JOIN category ON items.category_id=category.id")
	if err != nil {
		fmt.Printf("error querying items: %v\n", err)
		return r, err
	}
	var res ItemsList
	var items []ItemInfo
	var item ItemInfo
	for rows.Next() {
		err = rows.Scan(&item.Name, &item.CategoryName, &item.ImageFilename)
		if err != nil {
			fmt.Printf("error scanning rows: %v\n", err)
			return r, err
		}
		items = append(items, item)
	}
	res.Items = items
	return &res, err
}

func SearchItems(keyword string, db *sql.DB) (r *ItemsList, err error) {
	keyword = "%" + keyword + "%"
	rows, err := db.Query("SELECT items.name, category.name, image_name FROM items INNER JOIN category ON items.category_id=category.id WHERE items.name like ?", keyword)
	if err != nil {
		fmt.Printf("error querying data: %v\n", err)
		return r, err
	}
	var res ItemsList
	var items []ItemInfo
	var item ItemInfo
	for rows.Next() {
		err = rows.Scan(&item.Name, &item.CategoryName, &item.ImageFilename)
		if err != nil {
			fmt.Printf("error scanning rows: %v\n", err)
			return r, err
		}
		items = append(items, item)
	}
	res.Items = items
	return &res, err
}

func GetItemById(idx int, db *sql.DB) (r *ItemInfo, e error) {
	var item ItemInfo
	rows := db.QueryRow("SELECT items.name, category.name, image_name FROM items INNER JOIN category ON items.category_id=category.id WHERE items.id = ?", idx)
	err := rows.Scan(&item.Name, &item.CategoryName, &item.ImageFilename)
	if err != nil {
		fmt.Printf("error scanning rows: %v\n", err)
		return r, err
	}
	return &item, err
}
