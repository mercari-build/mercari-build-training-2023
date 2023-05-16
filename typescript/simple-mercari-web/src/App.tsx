import { useState } from 'react';
import './App.css';
import { ItemList } from './components/ItemList';
import { Listing } from './components/Listing';
import AppBar from '@mui/material/AppBar';
import { Typography } from '@mui/material';
import Toolbar from '@mui/material/Toolbar';
import Container from '@mui/material/Container';

function App() {
    // reload ItemList after Listing complete
    const [reload, setReload] = useState(true);
    return (
        <div>
            {/* <header className='Title'> */}
            {/* <p>
                    <b>Simple Mercari</b>
                </p> */}
            {/* </header> */}
            <AppBar position="static">
                <Toolbar>
                    <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}
                    >Simple Mercari</Typography>
                </Toolbar>
            </AppBar>
            <Container>
                <div>
                    <Listing onListingCompleted={() => setReload(true)} />
                </div>
                <div>
                    <ItemList reload={reload} onLoadCompleted={() => setReload(false)} />
                </div>
            </Container>
        </div>
    )
}

export default App;