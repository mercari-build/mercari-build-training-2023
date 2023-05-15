import React, { useEffect, useState } from 'react';

interface Item {
    id: number;
    name: string;
    category: string;
    image_filename: string;
};

const server = process.env.REACT_APP_API_URL || 'http://127.0.0.1:9000';
const placeholderImage = process.env.PUBLIC_URL + '/logo192.png';

interface Prop {
    reload?: boolean;
    onLoadCompleted?: () => void;
}

export const ItemList: React.FC<Prop> = (props) => {
    const { reload = true, onLoadCompleted } = props;
    const [items, setItems] = useState<Item[]>([])
    const fetchItems = () => {
        fetch(server.concat('/items'),
            {
                method: 'GET',
                mode: 'cors',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
            })
            .then(response => response.json())
            .then(data => {
                console.log('GET success:', data);
                setItems(data.items);
                onLoadCompleted && onLoadCompleted();
            })
            .catch(error => {
                console.error('GET error:', error)
            })
    }

    useEffect(() => {
        if (reload) {
            fetchItems();
        }
    }, [reload]);

    return (
        <div>
            {items.map((item) => {
                console.log(item.image_filename);
                return (
                    <div key={item.id} className='ItemList'>
                        <img src={server.concat('/image/', item.image_filename)} height="200" />
                        <p>
                            <span>{item.name}</span>
                            <br />
                            <span>Category: {item.category}</span>
                        </p>
                    </div>
                )
            })}
        </div>
    )
};
