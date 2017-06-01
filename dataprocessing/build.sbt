name := "dataprocessing"

version := "1.0"

scalaVersion := "2.11.8"

libraryDependencies ++= Seq(
	"com.typesafe" % "config" % "1.3.1",
	"com.datastax.cassandra" % "cassandra-driver-core" % "3.2.0",
	"com.datastax.cassandra" % "cassandra-driver-mapping" % "3.2.0",
	"com.datastax.spark" % "spark-cassandra-connector_2.10" % "2.0.1",
	"org.apache.spark" % "spark-sql_2.10" % "2.1.1" excludeAll ExclusionRule("org.apache.hadoop"),
	"org.apache.hadoop" % "hadoop-client" % "2.8.0"
)