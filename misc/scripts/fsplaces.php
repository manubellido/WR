<?php 

require('dbconn.inc');

$sql = "SELECT place_id FROM places_place";

$doc = array();

$res = pg_query($dbconn, $sql);

while($row = pg_fetch_assoc($res)) {
    $doc["places"][] = $row['place_id'];
}

header("Content-type: application/json");
echo json_encode($doc, JSON_PRETTY_PRINT);

?>
