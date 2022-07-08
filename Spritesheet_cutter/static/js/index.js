const canvas = new fabric.Canvas('canvas')

const imageInput = document.getElementById('image-input')
const detecionBtn = document.getElementById('detection-btn')
const clearBtn = document.getElementById('clear-btn')
const saveBtn = document.getElementById('save-btn')
const downloadForm = document.getElementById('download')

const check_plus_Input = document.getElementById('check-plus')
const check_minus_Input = document.getElementById('check-minus')
const transparent_bg = document.getElementById('set-transparent-bg')

const toleranci_Input = document.getElementById('toleranci')
const distance_Input = document.getElementById('distance')
const scale_percent_Input = document.getElementById('scale-percent')

// DEFAULT SETTINGS FOR DETECTION
let DISTANCE = 3
let TOLERANCI = 5
let SCALE_PERCENT = 100
let CHAR = '+'
let TRANSPARENT_BG = false
//

let detected_objects = [] // list of all detected objects

// IMAGE VARIABLES
let image = null
let img_x = img_y = 0
//

imageInput.addEventListener('change', function () {
  const reader = new FileReader()

  reader.addEventListener('load', () => {
    image = reader.result
    drawImageOnCanvas()
  })
  reader.readAsDataURL(this.files[0])
})

document.addEventListener('keydown', (event) => {
  // HANDLE REMOVE FROM CANVAS DETECTED OBJECTS

  const activateObject = canvas.getActiveObject()

  detected_objects = detected_objects.filter((item) => {
    return item != activateObject
  })

  if (activateObject) {
    canvas.remove(activateObject)
  }
})

canvas.on('mouse:wheel', (opt) => {
  // ZOOMING IMAGE

  const delta = opt.e.deltaY
  let zoom = canvas.getZoom()
  zoom *= 0.999 ** delta

  if (zoom > 20) zoom = 20
  if (zoom < 0.01) zoom = 0.01

  canvas.zoomToPoint({ x: opt.e.offsetX, y: opt.e.offsetY }, zoom)
  opt.e.preventDefault()
  opt.e.stopPropagation()
})

function drawImageOnCanvas () {
  if (image !== null) {
    fabric.Image.fromURL(image, function (img) {
      canvas.setBackgroundImage(img)
      canvas.centerObject(img)

      img_x = img.left
      img_y = img.top
    })
  }
}

detecionBtn.addEventListener('click', function () {
  if (image !== null) {
    $('#spinner').removeClass('hidden')

    isNumeric = (value) => { return /^-?\d+$/.test(value) }

    if (isNumeric(toleranci_Input.value)) TOLERANCI = Math.abs(toleranci_Input.value)
    else toleranci_Input.value = TOLERANCI

    if (isNumeric(distance_Input.value)) DISTANCE = Math.abs(distance_Input.value)
    else distance_Input.value = DISTANCE

    if (isNumeric(scale_percent_Input.value)) SCALE_PERCENT = Math.abs(scale_percent_Input.value)
    else scale_percent_Input.value = SCALE_PERCENT

    if (check_minus_Input.checked === true && check_plus_Input.checked === true) CHAR = '+-'
    else if (check_plus_Input.checked === true && check_minus_Input.checked === false) CHAR = '+'
    else if (check_minus_Input.checked === true && check_plus_Input.checked === false) CHAR = '-'

    if (transparent_bg.checked === true) TRANSPARENT_BG = true

    // SEND TO BACKEND
    $.ajax({
      type: 'POST',
      url: '/detection',
      contentType: 'application/json',
      data: JSON.stringify({
        'image':image,
        'scale-percent': SCALE_PERCENT,
        'toleranci': TOLERANCI,
        'distance': DISTANCE,
        'char': CHAR,
        'transparent-bg': TRANSPARENT_BG
      }),
      dataType: 'json',
      error: function (err) {
        console.log('Error:', err)
      }
    }).done(function (data) {
      // DATA FROM BACKEND
      $('#spinner').addClass('hidden')

      if (TRANSPARENT_BG) {
        image = 'data:image/png;base64,' + data.new_image
        drawImageOnCanvas()
      }

      const detected_objects_coords = data.coords

      detected_objects_coords.forEach(coords => {
        const x = coords[0] + Math.ceil(img_x) // plus rouding distance
        const y = coords[1] + Math.ceil(img_y) //
        const w = coords[2]
        const h = coords[3]

        // DRAW REACTS AROUND THE DETECTED OBJECTS
        const rect = new fabric.Rect({
          left: x,
          top: y,
          width: w,
          height: h,
          fill: '',
          stroke: 'black',
          strokeWidth: 1
        })

        canvas.add(rect)

        // ADD TO LST OF ALL OBJECTS
        detected_objects.push(rect)

        // VISIBILITY MANIPULATE POINTS OF REACTS
        rect.lockMovementX = true
        rect.lockMovementY = true

        rect.setControlsVisibility({
          tl: false,
          tr: false,
          bl: false,
          br: false,
          mtr: false
        })
      })
    })
  }
})

clearBtn.addEventListener('click', function () {
  // DELETE ALL DETECTED OBJECTS

  detected_objects.forEach(object => {
    canvas.remove(object)
  })
  detected_objects = []
})

function updateCoords (rect) {
  // get actual coords of detected image if user customize it
  // : return LIST

  if (detected_objects != []) {
    detected_objects_update = []

    detected_objects.forEach(rect => {
      const new_X = rect.left - Math.ceil(img_x)
      const new_Y = rect.top - Math.ceil(img_y)
      const new_W = rect.width * rect.scaleX
      const new_H = rect.height * rect.scaleY

      detected_objects_update.push([new_X, new_Y, new_W, new_H])
    })

    return detected_objects_update
  } else {
    alert('List of detected objects is empty')
  }
}

saveBtn.addEventListener('click', function () {
  // SAVE DETECTED IMAGES

  if (detected_objects !== [] && image !== null) {
    const actualCoords = updateCoords(detected_objects)

    $.ajax({
      type: 'POST',
      url: '/cut-image',
      contentType: 'application/json',
      data: JSON.stringify({
        'image': image,
        'coords': actualCoords
      }),
      dataType: 'json'

    }).done(function () {
      downloadForm.submit()
    }
    )
  }
})
