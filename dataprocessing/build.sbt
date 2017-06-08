name := "dataprocessing"

version := "1.0"

scalaVersion := "2.10.6"

resolvers += "Spark Packages Repo" at "https://dl.bintray.com/spark-packages/maven"

libraryDependencies ++= Seq(
	"com.typesafe" % "config" % "1.3.1",
	"com.datastax.cassandra" % "cassandra-driver-core" % "3.2.0",
	"com.datastax.cassandra" % "cassandra-driver-mapping" % "3.2.0",
	"datastax" % "spark-cassandra-connector" % "2.0.1-s_2.10",
	"org.apache.spark" % "spark-sql_2.10" % "2.1.0" excludeAll ExclusionRule("org.apache.hadoop"),
	"org.apache.hadoop" % "hadoop-client" % "2.8.0"
)