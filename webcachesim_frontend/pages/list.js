import { useState } from "react";
import Button from "@material-ui/core/Button";
import { makeStyles, withStyles } from "@material-ui/core/styles";
import Page from "../components/page";
import axios from "../axios";
import Tabs from "@material-ui/core/Tabs";
import Tab from "@material-ui/core/Tab";
import Typography from "@material-ui/core/Typography";
import Table from "@material-ui/core/Table";
import TableBody from "@material-ui/core/TableBody";
import TableCell from "@material-ui/core/TableCell";
import TableContainer from "@material-ui/core/TableContainer";
import TableHead from "@material-ui/core/TableHead";
import TableRow from "@material-ui/core/TableRow";
import Paper from "@material-ui/core/Paper";
import Snackbar from "@material-ui/core/Snackbar";
import { Line, Circle } from "rc-progress";
import { Switch } from "@material-ui/core";
import { Alert } from "@material-ui/lab";
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
  button: {}
}));

const AntTabs = withStyles({
  root: {
    borderBottom: "1px solid #e8e8e8"
  },
  indicator: {
    backgroundColor: "#1890ff"
  }
})(Tabs);

const AntTab = withStyles((theme) => ({
  root: {
    textTransform: "none",
    minWidth: 72,
    fontWeight: theme.typography.fontWeightRegular,
    marginRight: theme.spacing(4),
    "&:hover": {
      color: "#40a9ff",
      opacity: 1
    },
    "&$selected": {
      color: "#1890ff",
      fontWeight: theme.typography.fontWeightMedium
    },
    "&:focus": {
      color: "#40a9ff"
    }
  },
  selected: {}
}))((props) => <Tab disableRipple {...props} />);

function SnackAlert(props) {
  return <Alert variant="filled" {...props} />;
}

function PageTabs({}) {
  const classes = useStyles();
  const [value, setValue] = React.useState(0);
  const router = useRouter();
  const status = router.query.status || "created";
  const handleChange = (event, newValue) => {
    setValue(newValue);
  };
  const onClick = (status) => {
    console.log(router.pathname);
    router.push({
      pathname: "/list",
      query: { status },
      options: { shallow: true }
    });
  };

  const statusToIndex = {
    created: 0,
    running: 1,
    failed: 2,
    done: 3
  };
  return (
    <div>
      <div className={classes.demo1}>
        <AntTabs value={statusToIndex[status]} onChange={handleChange}>
          <AntTab label="Created" onClick={() => onClick("created")} />
          <AntTab label="Running" onClick={() => onClick("running")} />
          <AntTab label="Failed" onClick={() => onClick("failed")} />
          <AntTab label="Done" onClick={() => onClick("done")} />
        </AntTabs>
      </div>
    </div>
  );
}

function getTaskPercentage(task) {
  return (task["current_count"] / task["total_count"]) * 100;
}

function getTaskSecondsRemaining(task) {
  return (
    (task["total_count"] - task["current_count"]) / task["count_per_second"]
  );
}

function CreatedTable({ tasks }) {
  const classes = useStyles();
  const createdFields = ["task_id", "id", "parameters", "created_at"];
  return (
    <TableContainer component={Paper}>
      <Table className={classes.table} aria-label="simple table">
        <TableHead>
          <TableRow>
            {createdFields.map((field) => {
              return <TableCell>{field}</TableCell>;
            })}
          </TableRow>
        </TableHead>
        <TableBody>
          {tasks.map((task) => (
            <TableRow key={task.task_id}>
              {createdFields.map((field) => {
                return (
                  <TableCell classes={{ root: classes.row }}>
                    {JSON.stringify(task[field])}
                  </TableCell>
                );
              })}
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
}

function ListPage({ tasks, automaticState }) {
  const classes = useStyles();
  const router = useRouter();
  const [automaticOn, setAutomaticState] = useState(automaticState);
  const [open, setOpen] = useState(false);
  const taskFields = ["id", "parameters", "task_id"];
  const status = router.query.status || "created";
  const handleClose = (event, reason) => {
    if (reason === "clickaway") {
      return;
    }
    setOpen(false);
  };
  console.log(tasks[0]);
  const toggleAutomatic = async () => {
    const toggled = !automaticOn;
    setAutomaticState(toggled);
    await axios.post("tasks/automatic/", { state: toggled });
    setOpen(true);
  };

  let table;
  if (status === "created") {
    table = <CreatedTable tasks={tasks} />;
  } else {
    table = (
      <TableContainer component={Paper}>
        <Table className={classes.table} aria-label="simple table">
          <TableHead>
            <TableRow>
              <TableCell>number</TableCell>
              <TableCell>hostname</TableCell>
              {taskFields.map((field) => {
                return <TableCell>{field}</TableCell>;
              })}
              <TableCell>progress</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {tasks.map((task, index) => (
              <TableRow key={task.task_id}>
                <TableCell classes={{ root: classes.row }}>
                  {index + 1}
                </TableCell>
                <TableCell classes={{ root: classes.row }}>
                  {task["executing_host"]["hostname"]}
                </TableCell>
                {taskFields.map((field) => {
                  return (
                    <TableCell classes={{ root: classes.row }}>
                      {JSON.stringify(task[field])}
                    </TableCell>
                  );
                })}
                <TableCell>
                  <Line
                    percent={
                      (task["current_count"] * 100) / task["total_count"]
                    }
                  />
                  <p>
                    {getTaskPercentage(task)}% - {getTaskSecondsRemaining(task)}{" "}
                    seconds remaining
                  </p>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    );
  }

  return (
    <Page>
      <Snackbar open={open} autoHideDuration={6000} onClose={handleClose}>
        <SnackAlert onClose={handleClose} severity="success">
          Success!
        </SnackAlert>
      </Snackbar>
      <PageTabs />
      <Switch
        color={"primary"}
        checked={automaticOn}
        onChange={toggleAutomatic}
      />
      <Typography>Automatic is {automaticOn ? "on" : "off"}</Typography>
      {table}
    </Page>
  );
}

ListPage.getInitialProps = async (ctx) => {
  const resp = await axios.get("tasks/", {
    params: { status: ctx.query.status }
  });
  const automaticResp = await axios.get("tasks/automatic/");
  resp.data.tasks.sort(function(a, b) {
    let keyA = a["executing_host"]["hostname"],
      keyB = b["executing_host"]["hostname"];
    if (keyA < keyB) return -1;
    if (keyA > keyB) return 1;
    return 0;
  });

  return { tasks: resp.data.tasks, automaticState: automaticResp.data.state };
};

export default ListPage;
