Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.

Licensed under the MIT License.
You may not use this file except in compliance with the License.
A copy of the License is located in the "license" file accompanying this file.

This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.

# Lambda Concurrency Hunt

This code example illustrates a programmatic way to search through CloudWatch Metrics for Lambda concurrency spikes, then list the invocations and average duration for all functions during that period in order to troubleshoot unwanted spikes in Lambda Concurrency.

You can read more about this pattern in the blog post: [blog post]

## Getting Started

After you fulfill the pre-requisites, just enter

```python3 lambda-con-hunt.py```

### Prerequisites

* You'll need an AWS account and credentials with access to AWS CloudWatch metrics and Lambda to describe the list of functions
* You'll need to install [Python 3](https://www.python.org/downloads/) and the [AWS SDK for Python](https://aws.amazon.com/sdk-for-python/)

### Installing

* Install prequisites   
* [Configure](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html) AWS Python SDK with required credentials

## License

This project is licensed under the MIT-0 License - see the [LICENSE.md](LICENSE.md) file for details