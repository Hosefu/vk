default = '''
{"buttons":[],"one_time":true}
'''

exercise = '''
{
  "one_time": false,
  "inline": true,
  "buttons": [
    [{
      "action": {
        "type": "text",
        "label": "%s"
      },
      "color": "secondary"
    }],
    [{
      "action": {
        "type": "text",
        "label": "%s"
      },
      "color": "secondary"
    }],
    [{
      "action": {
        "type": "text",
        "label": "%s"
      },
      "color": "secondary"
    }],
    [{
      "action": {
        "type": "text",
        "label": "%s"
      },
      "color": "secondary"
    }]
  ]
}
'''

next = '''
{
  "one_time": false,
  "inline": true,
  "buttons": [
    [{
      "action": {
        "type": "text",
        "label": "Отмена"
      },
      "color": "negative"
    },
      {
        "action": {
          "type": "text",
          "label": "Продолжить"
        },
        "color": "positive"
      }]
  ]
}
'''

biotop = '''
{
  "one_time": false,
  "inline": true,
  "buttons": [
    [{
      "action": {
        "type": "text",
        "label": "Отмена"
      },
      "color": "negative"
    },
      {
        "action": {
          "type": "text",
          "label": "Да, начать БИОТОП!"
        },
        "color": "positive"
      }]
  ]
}
'''
