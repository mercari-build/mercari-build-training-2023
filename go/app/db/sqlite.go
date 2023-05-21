package db

import (
	"database/sql"
	"fmt"
	_ "github.com/mattn/go-sqlite3"
)

type ItemsDB struct {
	Db *sql.DB
}

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

func (s *ItemsDB) AddItemToDb(item *ItemInfo) error {
	// QueryRow executes a query that is expected to return at most one row.
	rows := s.Db.QueryRow("SELECT id FROM category WHERE name = ?", item.CategoryName)
	var categoryId int
	err := rows.Scan(&categoryId)
	// insert new category if doesn't exist
	if err != nil {
		r, e := s.Db.Exec("INSERT INTO category(name) VALUES (?)", item.CategoryName)
		if e != nil {
			fmt.Printf("error inserting category name: %v\n", e)
			return e
		}
		id, _ := r.LastInsertId()
		categoryId = int(id)
	}
	res, err := s.Db.Exec("INSERT INTO items(name, category_id, image_name) VALUES (?, ?, ?)", item.Name, categoryId, item.ImageFilename)
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

func (s *ItemsDB) GetAllItems() (r *ItemsList, e error) {
	rows, err := s.Db.Query("SELECT items.name, category.name, image_name FROM items INNER JOIN category ON items.category_id=category.id")
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

func (s *ItemsDB) SearchItems(keyword string) (r *ItemsList, err error) {
	keyword = "%" + keyword + "%"
	rows, err := s.Db.Query("SELECT items.name, category.name, image_name FROM items INNER JOIN category ON items.category_id=category.id WHERE items.name like ?", keyword)
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

func (s *ItemsDB) GetItemById(idx int) (r *ItemInfo, e error) {
	var item ItemInfo
	rows := s.Db.QueryRow("SELECT items.name, category.name, image_name FROM items INNER JOIN category ON items.category_id=category.id WHERE items.id = ?", idx)
	err := rows.Scan(&item.Name, &item.CategoryName, &item.ImageFilename)
	if err != nil {
		fmt.Printf("error scanning rows: %v\n", err)
		return r, err
	}
	return &item, err
}
