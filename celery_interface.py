# ！/usr/bin/env python
# encoding: utf-8
"""
@Author:
@File: celery.py
@Time: 2022/5/14 21:45
@Describe:
"""

from celery import Celery

app = Celery('tasks',
             broker='amqp://localhost',
             backend='redis://localhost',
             include=['Quant.tasks.tasks'])

# Optional configuration, see the application user guide.
app.conf.update(
    result_expires=3600,
)

if __name__ == "__main__":
    app.start()
