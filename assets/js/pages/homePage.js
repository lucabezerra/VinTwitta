import React from 'react';
import ReactDOM from 'react-dom';
import { Router, Route, IndexRoute, browserHistory, Link } from 'react-router';
import HomePageContainer from '../containers/HomePageContainer';
import DjangoCSRFToken from 'django-react-csrftoken';
import axios from 'axios';


class Home extends React.Component {
  render() {
    return (
      <div>
        <h2>Welcome to VinTwitta</h2>
        <p>This is a Django + React SPA (Single Page Application) that allows you to type any Twitter handle and
        fetch its 200 latest tweets, which will be stored in the database - click on <Link to="/tweets/addHandle">Add
        Twitter Handle</Link> to do it.</p>
        <p>After storing it, click on <Link to="/tweets/filters">Filter Stored Tweets</Link> to filter the tweets that
        are already on the database either by Twitter handle, date, text or hashtags.</p>
        <h3>Enjoy!</h3>
      </div>
    );
  }
}


class AddHandle extends React.Component {
  render() {
    return (
      <div>
        <p>Welcome, USER!</p>
        <p>Write a Twitter handle below to fetch its tweets.</p>
        <form method="POST" action="/tweets/process_add_handle/">
          <DjangoCSRFToken />
          <input type="hidden" name="user_id" value="1" />
          <input type="text" name="handleName" />
          <input type="submit" value="Fetch Tweets!" />
        </form>
      </div>
    );
  }
}

class FilterType extends React.Component {
  constructor() {
    super();
    this.state = {
      value: null,
    };
  }

  change(event){
    this.setState({value: event.target.value});
    console.log("Event:", event.target.value);
    console.log("State:", this.state);
    console.log("Value:", this.state.value);
  }

  render() {
    var divStyle = {
      margin: '5px',
      marginLeft: '10px',
    };

    return (
      <input type="radio" name="filterType" style={divStyle} value={this.props.value} onChange={this.change.bind(this)} />
    );
  }
}

class FilterField extends React.Component {
  constructor() {
    super();
    this.state = {
      shouldDisplay: false,
    };
  }

  toggleDisplay(props) {
    this.setState({shouldDisplay: props.show});
  }

  render() {
    return (
      <div name={this.props.divName} >
        {this.props.displayValue}: <input type={this.props.inputType} name={this.props.filterName} />
      </div>
    );
  }
}

class FilterResults extends React.Component {
  render() {
    return (
      <div>
        <h3>Tweets Filtered:</h3>
        <select name="filteredTweets" style={{ minWidth: "20%" }} size="10">
            <option name="tweet.id">tweet.text</option>
        </select>
      </div>
    );
  }
}

class FilterTweets extends React.Component {
  constructor() {
    super();

    this.state = {
    }
  }

  selectChange(event){
     this.setState({value: event.target.value});
  }

  filterChange() {
    if (this.props.filterName == "userFilter") {

    }
  }

  render() {
    return (
      <div>
        <p>Welcome, USER!</p>
        <p>Select a filter type and enter the corresponding filter data below.</p>
        <form method="POST" action="filters/user/lucabezerra_">
          <DjangoCSRFToken />
          <p>Filter by:</p>
          <br />
          <FilterField divName="userFilterDiv" displayValue="Username" inputType="text" filterName="userFilter" />
          <FilterField divName="dateFilterDiv" displayValue="Date" inputType="text" filterName="dateFilter" />
          <FilterField divName="textFilterDiv" displayValue="Text" inputType="text" filterName="textFilter" />
          <FilterField divName="hashtagFilterDiv" displayValue="Hashtag" inputType="text" filterName="hashtagFilter" />
          <br />
          <input type="submit" value="FILTER!" />
        </form>
        <br />
        <h3>Tweets Filtered:</h3>
        <select name="filteredTweets" style={{ minWidth: "20%" }} size="10">
            <option name="tweet.id">tweet.text</option>
        </select>
      </div>
    );
  }
}

class FilterByUser extends React.Component {
  constructor() {
    super();

    this.state = {
      username: "",
    };
  }

  fetchData() {
    axios.get('/tweets/filters/user/' + this.state.username + '/')
      .then(function (response) {
        console.log("Response", response);
      })
      .catch(function (error) {
        console.log("Error:", error);
    });
  }

  storeUsername(evt) {
    this.setState({
      username: evt.target.value
    });
  }

  render() {
    return (
      <div>
        <p>Filter by Username - Type the username below:</p>
        <br />
        Username: <input type="text" name="userFilter" onBlur={(evt) => this.storeUsername(evt)} />
        <br />
        <input type="button" onClick={() => this.fetchData()} value="FILTER!" />
        <br />
        <FilterResults />
      </div>
    );
  }
}


class App extends React.Component {
  render() {
    return (
      <div>
        <h1>VinTwitta</h1>
        <ul className="header">
          <li><Link activeClassName="active" to="/tweets">Home</Link></li>
          <li><Link activeClassName="active" to="/tweets/addHandle">Add Twitter Handle</Link></li>
          <li><Link activeClassName="active" to="/tweets/filters_user">Filter by Username</Link></li>
        </ul>
        <div className="content">
          {this.props.children}
        </div>
      </div>
    );
  }
}

ReactDOM.render(
  <Router history={browserHistory}>
    <Route path="/" component={App}></Route>
    <Route path="/tweets" component={App}>
      <IndexRoute component={Home} />
      <Route path="addHandle" component={AddHandle} />
      <Route path="filters_user" component={FilterByUser} />
    </Route>
  </Router>,
  document.getElementById('react-app')
);

//
//ReactDOM.render(
//  <div>
//    <App/>
//  </div>,
//  document.getElementById('react-app')
//);
