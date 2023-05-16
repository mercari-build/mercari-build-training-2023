import React, { useState } from 'react';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import Box from '@mui/material/Box';

const server = process.env.REACT_APP_API_URL || 'http://127.0.0.1:9000';

interface Prop {
    onListingCompleted?: () => void;
}

type formDataType = {
    name: string,
    category: string,
    image: string | File,
}

export const Listing: React.FC<Prop> = (props) => {
    const { onListingCompleted } = props;
    const initialState = {
        name: "",
        category: "",
        image: "",
    };
    const [values, setValues] = useState<formDataType>(initialState);

    const onValueChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        setValues({
            ...values, [event.target.name]: event.target.value,
        })
    };
    const onFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        setValues({
            ...values, [event.target.name]: event.target.files![0],
        })
    };
    const onSubmit = (event: React.FormEvent<HTMLFormElement>) => {
        event.preventDefault()
        const data = new FormData()
        data.append('name', values.name)
        data.append('category', values.category)
        data.append('image', values.image)

        console.log(values);
        fetch(server.concat('/items'), {
            method: 'POST',
            mode: 'cors',
            body: data,
        })
            .then(response => {
                console.log('POST status:', response.statusText);
                onListingCompleted && onListingCompleted();
            })
            .catch((error) => {
                console.error('POST error:', error);
            })
    };
    return (
        <Box
            sx={{
                '& .MuiTextField-root': { m: 1, width: '25ch' },
            }}
        >
            <form onSubmit={onSubmit}>
                <div>
                    <TextField
                        type="text"
                        required
                        name='name'
                        id='name'
                        placeholder="name"
                        variant="standard"
                        onChange={onValueChange}
                    />
                    <TextField
                        type="text"
                        name='category'
                        id='category'
                        placeholder="category"
                        variant="standard"
                        onChange={onValueChange}
                    />
                    <TextField
                        type="file"
                        required
                        name='image'
                        id='image'
                        placeholder="image"
                        variant="standard"
                        onChange={onFileChange}
                    />
                    <Button type="submit">List this item</Button>
                </div>
            </form>
        </Box>
    );
}
