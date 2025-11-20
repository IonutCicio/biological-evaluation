#!/bin/bash

use openbox
db.task.find().sort({create_time: -1}).limit(1)[0]._id
db.runhistory.find({task_id: "69147f79ffc036549f3a1ab9"}).sort({result: 1})[0].result
db.runhistory.find({task_id: "69147f79ffc036549f3a1ab9"}).sort({result: 1}).size()
db.runhistory.find({task_id: "69147f79ffc036549f3a1ab9"}).sort({result: 1}).limit(10).map(x => x.result[0])
db.runhistory.find({task_id: "69147f79ffc036549f3a1ab9"}).sort({result: 1}).map(x => x.result[0])

db.runhistory.find({task_id: "69148863ffc036549f3a1fb2"}).sort({result: 1})[0].result
db.runhistory.find({task_id: "69148863ffc036549f3a1fb2"}).sort({result: 1}).size()
db.runhistory.find({task_id: "69148863ffc036549f3a1fb2"}).sort({result: 1}).limit(10).map(x => x.result[0])
db.runhistory.find({task_id: "69148863ffc036549f3a1fb2"}).sort({result: 1}).map(x => x.result[0])

"6911aaacffc036549f39fa4c"/"69148863ffc036549f3a1fb2"

"6914b618ffc036549f3a25cf"

db.runhistory.find({task_id: "6914b618ffc036549f3a25cf"}).sort({result: 1})[0].result
db.runhistory.find({task_id: "6914b618ffc036549f3a25cf"}).sort({result: 1}).size()
db.runhistory.find({task_id: "6914b618ffc036549f3a25cf"}).sort({result: 1}).limit(10).map(x => x.result[0])
db.runhistory.find({task_id: "6914b618ffc036549f3a25cf"}).sort({result: 1}).map(x => x.result[0])

"69148863ffc036549f3a1fb2"/"6914b618ffc036549f3a25cf"
