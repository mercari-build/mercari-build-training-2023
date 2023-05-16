import React, { useEffect, useState } from 'react';
import Card from '@mui/material/Card';
import Typography from '@mui/material/Typography';
import CardMedia from '@mui/material/CardMedia';
import Grid from '@mui/material/Grid';
import SellIcon from '@mui/icons-material/Sell';


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
        <Grid container spacing={2} p={2} >
            {
                items.map((item) => {
                    console.log(item.image_filename);
                    return (
                        <Grid item xs={6} sm={3} key={item.id} >
                            <Card sx={{ minHeight: 200 }}>
                                <CardMedia
                                    component="img"
                                    height="200"
                                    src={server.concat('/image/', item.image_filename)}
                                    alt={item.name}
                                />
                                <Typography variant="h5" component="div" sx={{ p: 1 }}>
                                    {item.name}
                                </Typography>
                                <Typography sx={{ pl: 1 }} color="text.secondary" >
                                    <SellIcon fontSize="inherit" color="action" />
                                    {item.category}
                                </Typography>
                            </Card>
                        </Grid>
                    )
                })
            }
        </Grid >
    )
};
