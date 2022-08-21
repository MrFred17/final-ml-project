package com.eshqol.imagepickefinal

import android.annotation.SuppressLint
import android.content.Intent
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.os.Bundle
import android.provider.MediaStore
import android.util.Base64
import android.widget.Button
import android.widget.ImageView
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import androidx.appcompat.app.AppCompatDelegate
import androidx.core.graphics.drawable.toBitmap
import com.google.firebase.database.DataSnapshot
import com.google.firebase.database.DatabaseError
import com.google.firebase.database.ValueEventListener
import com.google.firebase.database.ktx.database
import com.google.firebase.database.ktx.getValue
import com.google.firebase.ktx.Firebase
import com.google.mlkit.vision.label.ImageLabeler
import com.google.mlkit.vision.label.ImageLabeling
import com.google.mlkit.vision.label.defaults.ImageLabelerOptions
import java.io.ByteArrayOutputStream



@Suppress("DEPRECATION")
class MainActivity : AppCompatActivity() {
    private val PICK_IMAGE = 1500
    private val CAMERA_REQUEST = 2000
    private lateinit var imageLabeler: ImageLabeler
    private var last = ""
    private var first = true
    private val database = Firebase.database


    @SuppressLint("SetTextI18n")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        this.title = "Machine Learning Project"

        AppCompatDelegate.setDefaultNightMode(AppCompatDelegate.MODE_NIGHT_NO)

        val image = findViewById<ImageView>(R.id.imageView2)
        imageLabeler = ImageLabeling.getClient(ImageLabelerOptions.DEFAULT_OPTIONS)


        val gallery = findViewById<Button>(R.id.button)
        val camera = findViewById<Button>(R.id.button2)

        gallery.setOnClickListener {
            pickImage("gallery")
        }

        camera.setOnClickListener {
            pickImage("camera")
        }


    }


    private fun pickImage(kind: String) {
        if (kind == "gallery"){
            val intent = Intent(Intent.ACTION_GET_CONTENT)
            intent.type = "image/*"
            startActivityForResult(intent, PICK_IMAGE)
        }
        else{
            val cameraIntent = Intent(MediaStore.ACTION_IMAGE_CAPTURE)
            startActivityForResult(cameraIntent, CAMERA_REQUEST)
        }
    }



    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)

        val image = findViewById<ImageView>(R.id.imageView2)

        if (requestCode == PICK_IMAGE && resultCode == RESULT_OK) {
            if (data == null) {
                return
            }

            val inputStream = contentResolver.openInputStream(data.data!!)
            val bitmap = BitmapFactory.decodeStream(inputStream)
            image.setImageBitmap(bitmap)
            makeTheMagic()

        }

        else if (requestCode == CAMERA_REQUEST && resultCode == RESULT_OK) {
            val bitmap = data!!.extras!!["data"] as Bitmap?

            image.setImageBitmap(bitmap)
            makeTheMagic()
        }

    }

    @SuppressLint("SetTextI18n")
    private fun makeTheMagic() {
        val image = findViewById<ImageView>(R.id.imageView2)
        val textResult = findViewById<TextView>(R.id.textView)
        val priceText = findViewById<TextView>(R.id.priceTextView)

        textResult.text = "Processing..."
        priceText.text = ""
        var bitmap = image.drawable.toBitmap()

        val oldSize = bitmap.byteCount
        if (oldSize > 10000000) {
            bitmap = getResizedBitmap(bitmap, 1000)
        }

        val baos = ByteArrayOutputStream()
        bitmap.compress(Bitmap.CompressFormat.JPEG, 80, baos)

        val byteArray = baos.toByteArray()
        val encoded = Base64.encodeToString(byteArray, Base64.DEFAULT)

        val myRef = database.getReference("message")
        myRef.setValue(encoded.toString())

        val ref = database.getReference("output")
        val refRefresh = database.getReference("refresh")
        refRefresh.setValue("True")


        ref.addValueEventListener(object : ValueEventListener {
            override fun onDataChange(dataSnapshot: DataSnapshot) {
                val data = dataSnapshot.getValue<String>().toString()
                if (first){
                    last = data
                    first = false
                }
                if (last != data){
                    last = data
                    if ("@" in data) {
                        val (sentence, price) = data.split('@')
                        textResult.text = sentence
                        if (price != "-1" && price != "- 1" && "-1" !in price) {
                            val p = price.replace(' ', '\n')
                            priceText.text = p
                        }
                    }
                    else {
                        textResult.text = data
                        priceText.text = ""
                    }
                }

            }

            override fun onCancelled(error: DatabaseError) {
            }
        })

    }

    private fun getResizedBitmap(image: Bitmap, maxSize: Int): Bitmap {
        var width = image.width
        var height = image.height
        val bitmapRatio = width.toFloat() / height.toFloat()
        if (bitmapRatio > 1) {
            width = maxSize
            height = (width / bitmapRatio).toInt()
        } else {
            height = maxSize
            width = (height * bitmapRatio).toInt()
        }
        return Bitmap.createScaledBitmap(image, width, height, true)
    }



}