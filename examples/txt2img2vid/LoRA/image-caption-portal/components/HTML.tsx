/**
 * Renders the HTML skeleton for the expanding card grid.
 * @returns The HTML skeleton component.
 */
export default function HTMLSketleton() {
    return (
        <div className="wrapper">

        <div className="header">
          <h1 className="header__title">Expanding Card Grid</h1>
          <h2 className="header__subtitle">with Flexbox</h2>
        </div>
      
        <div className="cards">
      
          <div className=" card [ is-collapsed ] ">
            <div className="card__inner [ js-expander ]">
              <span>Card</span>
              <i className="fa fa-folder-o"></i>
            </div>
            <div className="card__expander">
              <i className="fa fa-close [ js-collapser ]"></i>
              Expander
            </div>
          </div>
      
          <div className=" card [ is-collapsed ] ">
            <div className="card__inner [ js-expander ]">
              <span>Card</span>
              <i className="fa fa-folder-o"></i>
            </div>
            <div className="card__expander">
              <i className="fa fa-close [ js-collapser ]"></i>
              Expander
            </div>
          </div>
      
          <div className=" card [ is-collapsed ] ">
            <div className="card__inner [ js-expander ]">
              <span>Card</span>
              <i className="fa fa-folder-o"></i>
            </div>
            <div className="card__expander">
              <i className="fa fa-close [ js-collapser ]"></i>
              Expander
            </div>
          </div>
      
          <div className=" card [ is-collapsed ] ">
            <div className="card__inner [ js-expander ]">
              <span>Card</span>
              <i className="fa fa-folder-o"></i>
            </div>
            <div className="card__expander">
              <i className="fa fa-close [ js-collapser ]"></i>
              Expander
            </div>
          </div>
      
          <div className=" card [ is-collapsed ] ">
            <div className="card__inner [ js-expander ]">
              <span>Card</span>
              <i className="fa fa-folder-o"></i>
            </div>
            <div className="card__expander">
              <i className="fa fa-close [ js-collapser ]"></i>
              Expander
            </div>
          </div>
      
          <div className=" card [ is-collapsed ] ">
            <div className="card__inner [ js-expander ]">
              <span>Card</span>
              <i className="fa fa-folder-o"></i>
            </div>
            <div className="card__expander">
              <i className="fa fa-close [ js-collapser ]"></i>
              Expander
            </div>
          </div>
      
          <div className=" card [ is-collapsed ] ">
            <div className="card__inner [ js-expander ]">
              <span>Card</span>
              <i className="fa fa-folder-o"></i>
            </div>
            <div className="card__expander">
              <i className="fa fa-close [ js-collapser ]"></i>
              Expander
            </div>
          </div>
      
          <div className=" card [ is-collapsed ] ">
            <div className="card__inner [ js-expander ]">
              <span>Card</span>
              <i className="fa fa-folder-o"></i>
            </div>
            <div className="card__expander">
              <i className="fa fa-close [ js-collapser ]"></i>
              Expander
            </div>
          </div>
      
          <div className=" card [ is-collapsed ] ">
            <div className="card__inner [ js-expander ]">
              <span>Card</span>
              <i className="fa fa-folder-o"></i>
            </div>
            <div className="card__expander">
              <i className="fa fa-close [ js-collapser ]"></i>
              Expander
            </div>
          </div>
      
        </div>
      
      </div>
    );
  }