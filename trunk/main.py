#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#




import wsgiref.handlers
from django.utils import simplejson as json
from google.appengine.ext import webapp, db


class Data(db.Model):
  group = db.StringProperty()
  type = db.StringProperty()
  data = db.TextProperty()
  date = db.DateTimeProperty(auto_now_add=True)
  
def write(group, type, data):
  Data(group = group,
            type = type,
            data = data).put()
  return {'status': 200, 'group': group, 'type': type}
  
def list(group, type):
  list = []
  for obj in Data.gql("WHERE group = :1 AND type = :2 ORDER BY date DESC", group, type):
    list.append({'date': obj.date.isoformat(), 'id': obj.key().id()})
  return {'status': 200, 'list': list, 'group': group, 'type': type}

def idx(group, type, index):
  res = Data.gql("WHERE group = :1 AND type = :2 ORDER BY date DESC", group, type).fetch(1, int(index))
  if res[0]:
    return {'status': 200, 
            'key': res[0].key().id(), 
            'date': res[0].date.isoformat(), 
            'data': res[0].data, 
            'group': group, 
            'type': type}
  else:
    return {'status': 404, 'group': group, 'type': type}

def ridx(group, type, index):
  res = Data.gql("WHERE group = :1 AND type = :2 ORDER BY date ASC", group, type).fetch(1, int(index))
  if res[0]:
    return {'status': 200, 
            'key': res[0].key().id(), 
            'date': res[0].date.isoformat(), 
            'data': res[0].data, 
            'group': group, 
            'type': type}
  else:
    return {'status': 404, 'group': group, 'type': type}


def read(key):
  return {'status': 200, 'data': Data.get_by_id(int(key)).data, 'key': key}

def jsonp(self, data):
  if self.request.get("jsonp"):
    self.response.out.write(self.request.get("jsonp")+"(")
    self.response.out.write(json.dumps(data))
    self.response.out.write(")")
  else:
    self.response.out.write(json.dumps(data))

def handle(self):
  act = self.request.get("act")
  group = self.request.get("group")
  type = self.request.get("type")
  data = self.request.get("data")
  key = self.request.get("key")
  index = self.request.get("index")
  if act == "write":
    res = write(group, type, data)
  elif act == "list":
    res = list(group, type)
  elif act == "read":
    res = read(key)
  elif act == "idx":
    res = idx(group, type, index)
  elif act == "ridx":
    res = ridx(group, type, index)
  else:
    res = {'status': 404}
  jsonp(self, res)

class MainHandler(webapp.RequestHandler):
  def get(self):
    handle(self)
  def post(self):
    handle(self)
    


def main():
  application = webapp.WSGIApplication([('/', MainHandler)],
                                       debug=True)
  wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
  main()
