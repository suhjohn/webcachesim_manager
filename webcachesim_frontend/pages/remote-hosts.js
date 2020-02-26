import { useState } from "react";
import Button from "@material-ui/core/Button";
import { makeStyles, withStyles } from "@material-ui/core/styles";
import Page from "../components/page";
import axios from "../axios";
import Table from "@material-ui/core/Table";
import TableBody from "@material-ui/core/TableBody";
import TableCell from "@material-ui/core/TableCell";
import TableContainer from "@material-ui/core/TableContainer";
import TableHead from "@material-ui/core/TableHead";
import TableRow from "@material-ui/core/TableRow";
import { Typography } from "@material-ui/core";
import Paper from "@material-ui/core/Paper";
import Snackbar from "@material-ui/core/Snackbar";
import { Alert } from "@material-ui/lab";
import { ClipLoader } from "react-spinners";
import { useRouter } from "next/router";

const useStyles = makeStyles((theme) => ({
  page: {
    display: "flex",
    height: "100%",
    justifyContent: "center",
    alignItems: "center"
  },
  row: {
    fontSize: "10px",
    maxWidth: "200px",
    wordWrap: "break-word"
  },
  table: {
    minWidth: 650
  },
  button: {},
  loader: {
    width: "100px"
  }
}));

function SnackAlert(props) {
  return <Alert variant="filled" {...props} />;
}

function RemoteHosts({ remoteHosts }) {
  const classes = useStyles();
  const router = useRouter();
  const nodeFields = ["hostname", "capacity"];
  const [open, setOpen] = React.useState(false);
  const [loading, setLoading] = React.useState(false);

  const handleClose = (event, reason) => {
    if (reason === "clickaway") {
      return;
    }
    setOpen(false);
  };

  const onCreateClick = async () => {
    setLoading(true);
    await axios.post("tasks/nodes/", { remote_hosts: remoteHosts });
    setOpen(true);
    setLoading(false);
  };

  const onKillClick = async () => {
    const hostnames = remoteHosts.map((remoteHost) => {
      return remoteHost["hostname"];
    });
    setLoading(true);
    await axios.post("tasks/nodes/process/", {
      remote_host_names: hostnames
    });
    setOpen(true);
    setLoading(false);
  };

  const onCreateRepoClick = async () => {
    const hostnames = remoteHosts.map((remoteHost) => {
      return remoteHost["hostname"];
    });
    // {params: {foo: 'bar'}}
    setLoading(true);
    await axios.post("tasks/nodes/repository/", {
      remote_host_names: hostnames
    });
    setOpen(true);
    setLoading(false);
  };

  const onUpdateClick = async () => {
    const hostnames = remoteHosts.map((remoteHost) => {
      return remoteHost["hostname"];
    });
    // {params: {foo: 'bar'}}
    setLoading(true);
    await axios.patch("tasks/nodes/repository/", {
      remote_host_names: hostnames
    });
    setOpen(true);
    setLoading(false);
  };

  return (
    <Page>
      <Snackbar open={open} autoHideDuration={6000} onClose={handleClose}>
        <SnackAlert onClose={handleClose} severity="success">
          Success!
        </SnackAlert>
      </Snackbar>
      <Snackbar open={loading} autoHideDuration={6000}>
        <SnackAlert onClose={handleClose} severity="info">
          <ClipLoader
            css={classes.loader}
            size={25}
            //size={"150px"} this also works
            color={"#123abc"}
            loading={loading}
          />
          Executing
        </SnackAlert>
      </Snackbar>
      <Typography variant="h1">Manage Remote Hosts</Typography>
      <Button variant="contained" color="primary" onClick={onCreateClick}>
        Update Remote Hosts
      </Button>
      <Button variant="contained" color="primary" onClick={onKillClick}>
        Kill Running Webcachesim Processes
      </Button>
      <Button variant="contained" color="primary" onClick={onCreateRepoClick}>
        Create Repositories
      </Button>
      <Button variant="contained" color="primary" onClick={onUpdateClick}>
        Update Repositories
      </Button>
      <TableContainer component={Paper}>
        <Table className={classes.table} aria-label="simple table">
          <TableHead>
            <TableRow>
              {nodeFields.map((field) => {
                return <TableCell key={field}>{field}</TableCell>;
              })}
            </TableRow>
          </TableHead>
          <TableBody>
            {remoteHosts.map((node) => (
              <TableRow key={node.hostname}>
                {nodeFields.map((field) => {
                  return (
                    <TableCell key={field} classes={{ root: classes.row }}>
                      {node[field]}
                    </TableCell>
                  );
                })}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Page>
  );
}

RemoteHosts.getInitialProps = async (ctx) => {
  const nodesResp = await axios.get("tasks/nodes/");
  return { remoteHosts: nodesResp.data.nodes };
};

export default RemoteHosts;
