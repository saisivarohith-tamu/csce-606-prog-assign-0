$ bundle exec cucumber features --format html --out cucumber_report.html
Traceback (most recent call last):
  File "/Users/sutiiruma/work/assign0/latest/1/src/main.py", line 631, in <module>
    app.run(command)
  File "/Users/sutiiruma/work/assign0/latest/1/src/main.py", line 51, in run
    self.parse_command(command)
  File "/Users/sutiiruma/work/assign0/latest/1/src/main.py", line 85, in parse_command
    self.handle_login(parts[1:])
  File "/Users/sutiiruma/work/assign0/latest/1/src/main.py", line 123, in handle_login
    username, password = args
    ^^^^^^^^^^^^^^^^^^
ValueError: too many values to unpack (expected 2)
Traceback (most recent call last):
  File "/Users/sutiiruma/work/assign0/latest/1/src/main.py", line 631, in <module>
    app.run(command)
  File "/Users/sutiiruma/work/assign0/latest/1/src/main.py", line 51, in run
    self.parse_command(command)
  File "/Users/sutiiruma/work/assign0/latest/1/src/main.py", line 91, in parse_command
    self.handle_people(parts[1:])
  File "/Users/sutiiruma/work/assign0/latest/1/src/main.py", line 318, in handle_people
    if session_token not in self.sessions:
       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
TypeError: unhashable type: 'list'
┌──────────────────────────────────────────────────────────────────────────────┐
│ Share your Cucumber Report with your team at https://reports.cucumber.io     │
│                                                                              │
│ Command line option:    --publish                                            │
│ Environment variable:   CUCUMBER_PUBLISH_ENABLED=true                        │
│ cucumber.yml:           default: --publish                                   │
│                                                                              │
│ More information at https://cucumber.io/docs/cucumber/environment-variables/ │
│                                                                              │
│ To disable this message, specify CUCUMBER_PUBLISH_QUIET=true or use the      │
│ --publish-quiet option. You can also add this to your cucumber.yml:          │
│ default: --publish-quiet                                                     │
└──────────────────────────────────────────────────────────────────────────────┘