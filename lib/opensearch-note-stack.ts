import * as cdk from "aws-cdk-lib";
import { Duration, Stack, StackProps } from "aws-cdk-lib";
import { Construct } from "constructs";
import * as path from "path";

interface OpensearchNoteProps extends StackProps {
  opensearchDomain: string;
}

export class OpensearchNoteStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props: OpensearchNoteProps) {
    super(scope, id, props);

    // role for lambda to read opensearch
    const role = new cdk.aws_iam.Role(this, "RoleForLambdaQueryOpenSearch", {
      roleName: "RoleForLambdaQueryOpenSearch",
      assumedBy: new cdk.aws_iam.ServicePrincipal("lambda.amazonaws.com"),
    });

    // lambda function to query opensearch
    const func = new cdk.aws_lambda.Function(this, "LamdaQueryOpenSearch", {
      functionName: "LamdaQueryOpenSearch",
      memorySize: 512,
      timeout: Duration.seconds(10),
      code: cdk.aws_lambda.EcrImageCode.fromAssetImage(
        path.join(__dirname, "./../lambda")
      ),
      handler: cdk.aws_lambda.Handler.FROM_IMAGE,
      runtime: cdk.aws_lambda.Runtime.FROM_IMAGE,
      environment: {
        OPENSEARCH_DOMAIN: props.opensearchDomain,
        PYTHONPATH: "/var/task/package",
        REGION: this.region,
      },
      role: role,
    });

    // api gateway
    const apigw = new cdk.aws_apigateway.RestApi(this, "OpenSearchApi", {
      restApiName: "opensearch",
    });

    const resource = apigw.root.addResource("cdk-entest");

    resource.addMethod("GET", new cdk.aws_apigateway.LambdaIntegration(func));
  }
}

interface DDBStreamProps extends StackProps {
  openSearchDomain: string;
  tableArn: string;
  tableStreamArn: string;
}

export class DDBStreamStack extends Stack {
  constructor(scope: Construct, id: string, props: DDBStreamProps) {
    super(scope, id, props);

    // role for lambda to read opensearch
    const role = new cdk.aws_iam.Role(this, "RoleForLambdaIndexOpenSearch", {
      roleName: "RoleForLambdaIndexOpenSearch",
      assumedBy: new cdk.aws_iam.ServicePrincipal("lambda.amazonaws.com"),
    });

    // lambda function
    const func = new cdk.aws_lambda.Function(this, "LambdaIndexOpenSearch", {
      functionName: "LambdaIndexOpenSearch",
      memorySize: 512,
      timeout: Duration.seconds(10),
      code: cdk.aws_lambda.EcrImageCode.fromAssetImage(
        path.join(__dirname, "./../lambda-index-oss")
      ),
      handler: cdk.aws_lambda.Handler.FROM_IMAGE,
      runtime: cdk.aws_lambda.Runtime.FROM_IMAGE,
      environment: {
        OPENSEARCH_DOMAIN: props.openSearchDomain,
        PYTHONPATH: "/var/task/package",
        REGION: this.region,
      },
      role: role,
    });

    // existing ddb table
    const table = cdk.aws_dynamodb.Table.fromTableAttributes(
      this,
      "NoteTableStream",
      {
        tableArn: props.tableArn,
        tableStreamArn: props.tableStreamArn,
      }
    );

    // configure ddb stream to trigger lambda
    func.addEventSource(
      new cdk.aws_lambda_event_sources.DynamoEventSource(table, {
        startingPosition: cdk.aws_lambda.StartingPosition.LATEST,
        batchSize: 5,
        maxBatchingWindow: Duration.seconds(1),
        bisectBatchOnError: true,
        retryAttempts: 2,
        enabled: true,
      })
    );
  }
}
