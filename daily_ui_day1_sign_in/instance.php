<?php
use OpenCloud\Rackspace;
$client = new OpenCloud\OpenStack('{keystoneUrl}', array(
  'username' => '{username}',
  'password' => '{apiKey}',
  'tenantId' => '{tenantId}',
));
$service = $client->computeService('{catalogName}', '{region}', '{urlType}');
$server = $compute->server();

$server->create(array(
    'name'     => 'MyServer',
    'imageId'  => '{imageId}',
    'flavorId' => '{flavorId}',
));
session_start();
$_SESSION['myIP']=$server->ip();
echo $server->ip();
?>
