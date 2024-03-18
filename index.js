const express= require('express')
const app=express()
const port=5000
const mod=require('./mod')
const mongoose=require('mongoose')
const cors=require('cors')
const bodyParser= require('body-parser')

app.use(express.json())
app.use(bodyParser.json());

app.use(cors({ origin: 'http://localhost:3000' }));
mongoose.connect('mongodb+srv://jo214841:0ZpivnAfAY3nGu9P@cluster0.tv57fgu.mongodb.net/bus').then(()=>{
    console.log('database connection successfully!')
    app.listen(port,()=>{
        console.log('server is running in  port: ',port)
    
    })
}
)


app.get('/',(req,res) => {
    res.send('hi');
});

app.post('/makeAvail', async (req, res) => {
    const { licence_plate_number } = req.body;
    try {
        let user = await mod.findOne({ licence_plate_number });

        if (user) {
            user.isAvailable = true;
            await user.save();
            console.log('updated correctly')
            res.status(200).send('Updated successfully');
        } else {
            res.status(404).send('User not found');
        }
    } catch (error) {
        console.log(error);
        res.status(500).send('Server error');
    }
});

app.post('/addBus',(req,res)=>{
    const{bus_id,licence_plate_number,isAvailable}=req.body

    try{
        new_bus= new mod({
            bus_id,
            licence_plate_number,
            isAvailable:isAvailable||false
        })

        new_bus.save()
        .then(()=>{
            console.log('insertion successfull')
            return res.status(200).json(new_bus)
            
        })
        .catch(err=>{
            console.log(err)
            return res.status(200).json({error:'internal error',details:err.message})
        })

        
        
    }
    catch(error)
        {
            console.log(error)
            res.status(500).json({ error: 'Internal Server Error' });

        }

})


