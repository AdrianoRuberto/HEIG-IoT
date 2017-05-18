import org.apache.spark.{SparkConf, SparkContext}
import com.datastax.spark.connector._
import com.datastax.spark.connector.rdd.CassandraTableScanRDD //Loads implicit functions

object Scripts extends App {

	val keyspaceName = "data"

	val conf: SparkConf = new SparkConf(true)
		.set("spark.cassandra.connection.host", "127.0.0.1:9042")
		.set("spark.cassandra.auth.username", "cassandra")
		.set("spark.cassandra.auth.password", "cassandra")

	val sc = new SparkContext("spark://192.168.123.10:7077", "test", conf)

	// Lis table event et compute
	def computeDelta(from: Int, to: Int) = {
		val events: CassandraTableScanRDD[CassandraRow] = sc.cassandraTable(keyspaceName, "events")
		events.where("timestamp > ? AND timestamp < ?", from, to)
	}

}
