const mongoose=require('mongoose')
const Schema=mongoose.Schema
const busSchema=new Schema({
    bus_id:{
        type:Number,
        required:true,
    },
    licence_plate_number:{
        type: String,
        required: true,
    },
    isAvailable:{
        type:Boolean,
        required:true,
    }
})

module.exports =mongoose.model('bus_data',busSchema)