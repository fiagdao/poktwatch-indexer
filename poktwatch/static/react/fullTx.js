
function Navbar {
  return (
    <div class="card-header sticky-card-header d-flex justify-content-between p-0">

      <ul class="nav nav-custom nav-borderless nav_tabs1" id="nav_tabs" role="tablist">
        <li class="nav-item">
          <a class="nav-link active" id="home-tab" data-toggle="tab" href="#home" aria-controls="home" aria-selected="true" onclick="javascript:updatehash('');">Overview</a>
        </li>
      </ul>
    </div>
  )
}



function Transaction(props) {

}

<div class="card">

  <Navbar />


  <div class="tab-content" id="myTabContent">

    <div class="tab-pane fade show active" id="home" role="tabpanel" aria-labelledby="home-tab">

      <div id="ContentPlaceHolder1_maintable" class="card-body">

        <div class="row align-items-center mt-1">
          <div class="col-md-3 font-weight-bold font-weight-sm-normal mb-1 mb-md-0"><i class='fal fa-question-circle text-secondary d-sm-inline-block mr-1' data-container='body' data-toggle='popover' data-placement='top'
              data-original-title='' title='' data-content='A TxHash or transaction hash is a unique 66 characters identifier that is generated whenever a transaction is executed.'></i>Transaction
            Hash:</div>
          <div class="col-md-9">
            <span id='spanTxHash' class='mr-1'>{{hash}}</span>

            <a class="js-clipboard text-muted" href="javascript:;" data-toggle="tooltip" title="Copy Txn Hash to clipboard" data-content-target="#spanTxHash" data-class-change-target="#spanTxHashLinkIcon" data-success-text="Copied"
              data-default-class="far fa-copy" data-success-class="far fa-check-circle">
              <span id="spanTxHashLinkIcon" class="far fa-copy"></span>
            </a>

          </div>
        </div>


        <hr class='hr-space'>
        <div class='row align-items-center mn-3'>
          <div class='col-auto col-md-3 font-weight-bold font-weight-sm-normal mb-1 mb-md-0'><i class='fal fa-question-circle text-secondary d-sm-inline-block mr-1' data-container='body' data-toggle='popover' data-placement='top'
              data-original-title='' title='' data-content='The status of the transaction.'></i>Status:</div>
          <div class='col col-md-9'>
              {%if code == 0 %}
              <span class='u-label u-label--sm u-label--success rounded' data-toggle='tooltip' title='A Status code indicating if the top-level call succeeded or failed (applicable for Post BYZANTIUM blocks only)'>
                <i class='fa fa-check-circle mr-1'></i>Success
              </span>
              {%elif code > 0%}
              <span class='u-label u-label--sm u-label--danger rounded' data-toggle='tooltip' title='A Status code indicating if the top-level call succeeded or failed (applicable for Post BYZANTIUM blocks only)'>
                <i class="fa fa-times-circle mr-1"></i>Fail with code '{{code}}'
              </span>
              {%else%}
              <span class="u-label u-label--sm u-label--secondary rounded"><i class="fa fa-dot-circle mr-1"></i> Pending</span>
              {%endif%}
            </span>
          </div>
        </div>

        <hr class="hr-space">

        <div class="row align-items-center">
          <div class="col-md-3 font-weight-bold font-weight-sm-normal mb-1 mb-md-0"><i class='fal fa-question-circle text-secondary d-sm-inline-block mr-1' data-container='body' data-toggle='popover' data-placement='top'
              data-original-title='' title='' data-content='The number of the block in which the transaction was recorded. Block confirmation indicate how many blocks since the transaction is mined.'></i>Block:</div>
          {%if code == -1%}
          <div class="col-md-9">
            <div class="col-md-9">
              (<i>Pending</i>)
              </div>
          </div>
          {%else %}
          <div class="col-md-9">
            <a href='/block/{{height}}'>{{height}}</a>
          </div>
          {%endif%}
        </div>

        <!-- <div id="ContentPlaceHolder1_divTimeStamp">
                        <hr class="hr-space">

                        <div class="row align-items-center">
                            <div class="col-md-3 font-weight-bold font-weight-sm-normal mb-1 mb-md-0"><i class='fal fa-question-circle text-secondary d-sm-inline-block mr-1' data-container='body' data-toggle='popover' data-placement='top' data-original-title='' title='' data-content='The date and time at which a transaction is mined.'></i>Timestamp:</div>
                            <div class="col-md-9">
                                <span id="clock"></span><i class='far fa-clock small mr-1'></i>40 secs ago (Oct-25-2021 11:13:38 PM +UTC)<span class='text-secondary ml-2 d-none d-sm-inline-block' title='Estimated duration between time First Seen and included in block'> | <i class='fal fa-stopwatch ml-1'></i> Confirmed within 30 secs</span>
                            </div>
                        </div>

                    </div> -->
        <hr class="hr-space">

        <div class="row align-items-center">
          <div class="col-md-3 font-weight-bold font-weight-sm-normal mb-1 mb-md-0"><i class='fal fa-question-circle text-secondary d-sm-inline-block mr-1' data-container='body' data-toggle='popover' data-placement='top'
              data-original-title='' title='' data-content='The sending party of the transaction (could be from a contract address).'></i>From:</div>
          <div class="col-md-9">
            <span id='spanFromAdd' style='display:none;'>{{sender}}</span><a id='addressCopy' class='mr-1' href='/address/{{sender}}'>{{sender}}</a>

            <a class="js-clipboard text-muted ml-1" href="javascript:;" data-toggle="tooltip" title="Copy From Address to clipboard" data-content-target="#spanFromAdd" data-class-change-target="#fromAddressLinkIcon" data-success-text="Copied"
              data-default-class="far fa-copy" data-success-class="far fa-check-circle">
              <span id="fromAddressLinkIcon" class="far fa-copy"></span>
            </a>

          </div>
        </div>

        {% if type == "send" %}
        <hr class="hr-space">
        <div class="row">
          <div class="col-md-3 font-weight-bold font-weight-sm-normal mb-1 mb-md-0"><i class='fal fa-question-circle text-secondary d-sm-inline-block mr-1' data-container='body' data-toggle='popover' data-placement='top'
              data-original-title='' title='' data-content='The receiving party of the transaction (could be a contract address).'></i>To:</div>
          <div class="col-md-9">
            <a id='contractCopy' href='/address/{{receiver}}' class='wordwrap mr-1'>{{receiver}}</a><span id='spanToAdd' style='display:none;'>{{receiver}}</span> <a class='js-clipboard text-muted ml-1' href='javascript: ;'
              data-toggle='tooltip' title='Copy To Address to clipboard' data-content-target='#spanToAdd' data-class-change-target='#spanToAddResult' data-success-text='Copied' data-default-class='far fa-copy'
              data-success-class='far fa-check-circle'> <span id='spanToAddResult' class='far fa-copy'></span> </a>
          </div>
        </div>
        {% endif %}


        <hr class="hr-space">

        <div class="row align-items-center mn-3">
          <div class="col-md-3 font-weight-bold font-weight-sm-normal mb-1 mb-md-0"><i class='fal fa-question-circle text-secondary d-sm-inline-block mr-1' data-container='body' data-toggle='popover' data-placement='top'
              data-original-title='' title='' data-content='The value being transacted in POKT and fiat value. Note: You can click the fiat value (if available) to see historical value at the time of transaction.'></i>Value:</div>
          <div class="col-md-9">
            <span id="ContentPlaceHolder1_spanValue"><span data-toggle='tooltip' title='The amount of Pokt to be transferred to the recipient with the transaction'><span
                  class='u-label u-label--value u-label--secondary text-dark rounded mr-1'>{{value|div:1000000}} Pokt</span></span>

            </span>
            <script type="text/javascript">
              console.log('asdfffffffffffff')

              function httpGet(theUrl) {
                var xmlHttp = new XMLHttpRequest();
                xmlHttp.open("GET", theUrl, false); // false for synchronous request
                xmlHttp.send(null);
                return xmlHttp.responseText;
              }
              var datal = await httpGet('https://thunderheadotc.io/api/price/')
              await new Promise(r => setTimeout(r, 2000));
              console.log(datal)
              var value = parseFloat(document.querySelector('#ContentPlaceHolder1_spanValue > span > span').innerText.slice(0, -4))
              console.log(value)
              document.querySelector('#ContentPlaceHolder1_spanValue > span').innerText += (value * datal["price"])
            </script>
          </div>
        </div>

        <div id="ContentPlaceHolder1_divTxFee">
          <hr class="hr-space">

          <div class="row align-items-center">
            <div class="col-md-3 font-weight-bold font-weight-sm-normal mb-1 mb-md-0"><i class='fal fa-question-circle text-secondary d-sm-inline-block mr-1' data-container='body' data-toggle='popover' data-placement='top'
                data-original-title='' title='' data-content='Amount paid to the miner for processing the transaction.'></i>Transaction
              Fee:</div>
            <div class="col-md-9">
              <span id="ContentPlaceHolder1_spanTxFee"><span data-toggle='tooltip' title='(Block Base Fee Per Gas + MaxPriorityFee Per Gas) * Gas Used'>{{fee|div:1000000}} Pokt </span></span>
            </div>
          </div>

        </div>

        <hr class='hr-space'>
        <div class='row align-items-center'>
          <div class='col-md-3 font-weight-bold font-weight-sm-normal mb-1 mb-md-0'><i class='fal fa-question-circle text-secondary d-sm-inline-block mr-1' data-container='body' data-toggle='popover' data-placement='top'
              data-original-title='' title='' data-content='Introduced in EIP2718, this defines a transaction type that is an envelope for current and future transaction types.'></i>Txn
            Type:</div>
          <div class='col-md-9'>{{type}}</div>
        </div>
      </div>
    </div>
  </div>
</div>
