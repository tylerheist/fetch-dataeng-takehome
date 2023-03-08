# Fetch Rewards Take Home for Data Engineering Role

## Description

This is my submission of a take-home assignment for a data engineering position at [Fetch Rewards](https://fetch.com/).

## How to Run

First, you'll want to clone this git repository and enter this top-level directory where you can find this `Readme.md`. 

I used `poetry` to manage my python project (highly recommend checking it out) - You can follow the installer guider [here](https://python-poetry.org/docs/).

Once you have `poetry` installed and you're in this directory, you want to start up the docker images provided using the configuration found in the `docker-compose.yml` file. You can do this by running:
```
$ docker compose up
```

Once the postgres and localstack instances are up and running locally, you can launch the ETL process I've created simply by running:
```
$ make run
```
Feel free to check out the `Makefile` if you're interested - all that the run command alias is doing is running the `app.py` file defined in `fetchrewards_takehome` directory in an venv using `poetry`. 

## Questions to answer 
I'm pulling these from the prompt (`prompt.pdf`) that I was given for the take home.

1. How would you deploy this application in production?

Answer: My first thought for this would probably be to deploy this in an AWS Lambda and have it be orchestrated on a cron schedule, depending on the business need. 

It could also be orchestrated in an airflow dag and run at a frequency dependent on some threshold about the SQS queue that can be monitored upstream in the same dag (e.g., run once the oldest message is X hours away from the retention threshold). 

2. What other components would you want to add to make this production ready?

Answer: Broadly, I'd want a lot of the same things I mentioned below in the "Next Steps" section - particularly around error handling. I would want some additional redundancy if a particular message wasn't handled appropriately and I would want potentially another process to be able to re-try these failed messages. I'd probably also want to get some CI/CD set-up long before this hit production.

I'd also want to think about the metrics of this ETL process and how we could report on them before we launched this into production (e.g., APM metrics in something like Datadog, an alerting system in something like pagerduty if this data is critical to the business)

3. How can this application scale with a growing dataset?

Answer: if we kept the architecture and approach approximately the same (batch, etc.), an easy way to scale the application would be to increase the number of AWS Lambda instances we throw at it at a time - we'd need some additional handling for batching the jobs across Lambdas, but it would not be difficult to adapt to that from the given approach.

Another way to address scale would be to take a new approach and think if we could decouple the stages of ETL or shift to an ELT approach - using streaming (e.g., Kafka), we could dump SQS messages as they are recieved in a staging database and hold them until we were able to run a larger transformation in a more efficient way (assuming this would be possible to delay given the business usecase/need for this data)

4. How can PII be recovered later on?

Answer: I used [Fernet encryption](https://cryptography.io/en/latest/fernet/) to mask the PII data, which is a symmetric encryption method. Therefore, using the same key seeded during encryption, you would be able to decrypt the encrypted data later on. I'll say that I haven't personally used this before in my experience and have more work experience "destructively" masking data using something like SHA256 hashing. 

5. What are the assumptions you made?

Answer: I've added a number of my assumptions to the code inline with sort of where I made them, but I will say here that I think the single biggest assumption I've made is that the business need for this data is such that the batch processing approach that I've taken here is reasonable. For example, if there were another consumer of this data who needed the ability to get the masked columns rapidly, it's possible that the batched approach taken here wouldn't allow for that consumer to receive the data within a reasonable SLA given their usecase. 

## Next Steps
- Handling errors and more logging: I currently have limited print statements to indicate the relative success or state of my program after each layer in the ETL process, but this is very minimal and should be improved. Additionally, I have almost no handling if anything were to go wrong (e.g., the number of messages extracted was higher than the number written to postgres) - the one bit of handling that I do have is to log the `ReceiptHandles` of SQS messages that were unable to be deleted so that they could handled outside the realm of this process (but this is not satisfactory).
- Testing: I created some really simple tests mostly to make sure that I knew how to access the resources available in the provided docker images easily, but didn't really have the time to go back to add tests that I think would be more valuable in testing my logic. 
- Input handling: Many of my functions could benefit from additional (or ANY) checks that the input given to them is reasonable and expected.
- Dataframe schema checks: I had a co-worker recently get me into [pandera](https://pandera.readthedocs.io/en/stable/) and I think that the code I've written here would benefit a lot from run-time checks against expected schemas (e.g., what it should look like post extract, or post transform)
- "Developer productivity"-style enhancements: While I used black, isort, and flake here, it would be nice to also conform to mypy and pydocstyle standards and also have all these tools running via pre-commit (just not nearly enough time to get that set-up)